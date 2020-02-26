#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2016 L3i - University of La Rochelle, France
#          Joseph Chazalon joseph(dot)chazalon(at)univ-lr(dot)fr
# Tool to detect and dewarp (correct perspective transform) a document
# page area in a mobile captured image.


# ==============================================================================
# Imports
import sys
import argparse
import logging
from collections import namedtuple
import json

import cv2
import numpy as np


# ==============================================================================
# Constants
PROG_VERSION = "0.1"
PROG_NAME = "Auto page dewarp"

EXITCODE_OK = 0
EXITCODE_INVALIDINPUTFILE = 10
EXITCODE_OUTPUTERROR = 20
EXITCODE_DOCNOTFOUND = 100
EXITCODE_UNKERR = 254


# ==============================================================================
# Types
# Simple 2D point
Pt = namedtuple("Pt", ["x", "y"])

# ==============================================================================
# Constants which should be parameters
# This version produces a fixed image size, this should be improved
w_A4_page=2480
h_A4_page=3506
num_pyrdown = 2

# ==============================================================================
def _scaleCoord(coord):
    return coord * 2**num_pyrdown

# ==============================================================================
def process_image(input_path, output_path, logger, gui=False):
    # Open image
    img = cv2.imread(input_path)
    if img is None:
        logger.errort("Cannot read input file.") 
        return EXITCODE_INVALIDINPUTFILE
    # orig_img = img.copy()
    # Downsample
    for _q in range(num_pyrdown):
        img = cv2.pyrDown(img)
    # Identify central point
    (height, width, _d) = img.shape
    cx = width/2
    cy = height/2
    # Binarize
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    closed = cv2.morphologyEx(hls[:,:,1], cv2.MORPH_CLOSE, np.ones((3,3),np.uint8),iterations=5)
    blurred = cv2.blur(closed,(3,3))
    bin = cv2.Canny(blurred, 0, 95,3 )
    # Extract contours
    binc=bin.copy()
    contours, _hierarchy = cv2.findContours(binc,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    # !!! Quit if nothing found
    if len(contours) <= 0:
        logger.error("Cannot find regions, not enough contrast.")
        return EXITCODE_DOCNOTFOUND

    # Filter contours around center point
    H=[]
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        dist = cv2.pointPolygonTest(hull,(cx,cy),False)
        if dist>0:
            H.append(hull)
    dists = [cv2.pointPolygonTest(x,(cx,cy),True) for x in H]
    idx=sorted(range(len(dists)), key=lambda k: dists[k])

    point_tl = None
    point_bl = None
    point_br = None
    point_tr = None

    # If no match, allow for closest contours
    # TODO make an option out of that
    if len(idx)==0:
        # dists1 = map(lambda x: cv2.arcLength(x,False), contours)
        dists1 = [cv2.arcLength(x,False) for x in contours]
        idx1 = sorted(range(len(dists1)), key=lambda k: dists1[k])
        if len(contours) >=1:
            if len(contours)>=3:
                H=[contours[idx1[-1]], contours[idx1[-2]], contours[idx1[-3]]]
            else:
                H=[contours[idx1[-1]]]
            # dists = map(lambda x: cv2.pointPolygonTest(x,(cx,cy),True), H)
            dists = [cv2.pointPolygonTest(x,(cx,cy),True) for x in H]
            idx=sorted(range(len(dists)), key=lambda k: dists[k])

    else: # len(idx) > 0:
        # Polygonal approximation and corner assignment
        approx = cv2.approxPolyDP(H[idx[0]],0.1*cv2.arcLength(H[idx[0]],True),True)
        if len(approx)==4:
            xs=[approx[0][0][0],approx[1][0][0],approx[2][0][0],approx[3][0][0]]
            ys=[approx[0][0][1],approx[1][0][1],approx[2][0][1],approx[3][0][1]]
            idx=sorted(range(len(ys)), key=lambda k: ys[k])
            top=[[xs[idx[0]],ys[idx[0]]],[xs[idx[1]],ys[idx[1]]]]
            bottom=[[xs[idx[2]],ys[idx[2]]],[xs[idx[3]],ys[idx[3]]]]
            if top[0][0]>top[1][0]:
                TL=top[1]
                TR=top[0]
            else:
                TL=top[0]
                TR=top[1]
            if bottom[0][0]>bottom[1][0]:
                BL=bottom[1]
                BR=bottom[0]
            else:
                BL=bottom[0]
                BR=bottom[1]

            # NOTE: Aspect ratio control could be added here

            # Assign real coordinates
            point_tl = Pt(x=_scaleCoord(TL[0]), y=_scaleCoord(TL[1]))
            point_bl = Pt(x=_scaleCoord(BL[0]), y=_scaleCoord(BL[1]))
            point_br = Pt(x=_scaleCoord(BR[0]), y=_scaleCoord(BR[1]))
            point_tr = Pt(x=_scaleCoord(TR[0]), y=_scaleCoord(TR[1]))

    # Estimate perspective transform
    logger.info("Found document - tl:(%-4.2f,%-4.2f) bl:(%-4.2f,%-4.2f)" 
                " br:(%-4.2f,%-4.2f) tr:(%-4.2f,%-4.2f)",
                point_tl.x, point_tl.y, point_bl.x, point_bl.y, 
                point_br.x, point_br.y, point_tr.x, point_tr.y)

    with open(output_path, 'w') as out_file:
        json.dump({
                'tl': {'x': int(point_tl.x), 'y': int(point_tl.y)},
                'bl': {'x': int(point_bl.x), 'y': int(point_bl.y)},
                'br': {'x': int(point_br.x), 'y': int(point_br.y)},
                'tr': {'x': int(point_tr.x), 'y': int(point_tr.y)}
            },
            out_file)

    # target_quad = np.float32([[1, 1], [1, h_A4_page], [w_A4_page, h_A4_page], [w_A4_page, 1]])
    # detect_quad = np.array([point_tl, point_bl, point_br, point_tr], np.float32)
    # trans_inv = cv2.getPerspectiveTransform(detect_quad, target_quad)
    # # Apply inverse transform
    # dst = cv2.warpPerspective(orig_img, trans_inv, (w_A4_page, h_A4_page))

    # Save the result
    # try:
    #     cv2.imwrite(output_path, dst)
    #     logger.debug("Wrote result to '%s'.", output_path)
    # except:
    #     logger.error("Could not save the result to '%s'.", output_path)
    #     return EXITCODE_OUTPUTERROR

    # Optionnal GUI display
    # if gui:
    #     win_orig = "Original"
    #     win_dete = "Detection"
    #     win_resu = "Result"
    #     cv2.namedWindow(win_orig, cv2.WINDOW_NORMAL)
    #     cv2.namedWindow(win_dete, cv2.WINDOW_NORMAL)
    #     cv2.namedWindow(win_resu, cv2.WINDOW_NORMAL)
    #     cv2.imshow(win_orig, orig_img)
    #     # Draw detected quad
    #     dgbq = np.int32([point_tl, point_bl, point_br, point_tr])
    #     cv2.polylines(orig_img, [dgbq], True, (0, 255, 0), 2)
    #     for txt, pt in [("TL", point_tl), ("TR", point_tr), ("BL", point_bl), ("BR", point_br)]:
    #         cv2.putText(orig_img, txt.upper(), (int(pt.x), int(pt.y)), cv2.FONT_HERSHEY_PLAIN, 2, (64, 255, 64), 2)
    #     cv2.imshow(win_dete, orig_img)
    #     cv2.imshow(win_resu, dst)
    #     key = None
    #     logger.info("Press 'q' or ESC to quit.")
    #     while key is None or key & 0xFF not in [ord('q'), ord(' '), 27]:
    #         key = cv2.waitKey(5000)

    # Exit properly
    return EXITCODE_OK

# ==============================================================================
def main():
    # Option parsing
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=('Detect and dewarp (correct perspective transform) a document'
                     ' page area in a mobile captured image.'))
    parser.add_argument('-d', '--debug', 
        action="store_true", 
        help="Activate debug output.")
    # parser.add_argument('-g', '--gui', 
    #     action="store_true", 
    #     help="Activate GUI to visualize output.")
    parser.add_argument('input_image', 
        help='Input image containing a document page.')
    # parser.add_argument('output_image', 
    #     help='Path to the place where the dewarped image should be stored.')
    parser.add_argument('output_file', 
        help='Path to output JSON file.')
    args = parser.parse_args()
    # Prepare logger
    logger = logging.getLogger(__name__)
    format="%(name)-12s %(levelname)-7s: %(message)s" #%(module)-10s
    formatter = logging.Formatter(format)    
    ch = logging.StreamHandler()  
    ch.setFormatter(formatter)  
    logger.addHandler(ch)
    level = logging.DEBUG if args.debug else logging.INFO
    logger.setLevel(level)
    # Run process
    # return process_image(args.input_image, args.output_image, logger, gui=args.gui)
    return process_image(args.input_image, args.output_file, logger, None)

if __name__ == "__main__":
    ret = main()
    if ret is not None:
        sys.exit(ret)
