import argparse
import glob
import json
import os
import pickle

import cv2
import dlib
import numpy as np


def show_video(images, groundtruth=None):
    for i, image in enumerate(images):

        if groundtruth and i < len(groundtruth):
            x, y, w, h = groundtruth[i]
            cv2.rectangle(image, (x, y), (x + w, y+h), (255, 0, 255), 2)

        cv2.imshow('frame', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


def read_data(video_name):
    image_files = glob.glob('datasets/vtb/{}/img/[0-9]*.jpg'.format(video_name))
    image_files.sort()
    images = [cv2.imread(image_file) for image_file in image_files]

    groundtruth_files = glob.glob('datasets/vtb/{}/groundtruth_rect.*'.format(video_name))
    print("Reading {} and {}".format(video_name, groundtruth_files))

    groundtruth_list = [np.loadtxt(groundtruth_file, dtype=int).tolist() for groundtruth_file in groundtruth_files]
    return images, groundtruth_list


def accuracy(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    area1 = w1 * h1
    area2 = w2 * h2
    right1 = x1 + w1
    right2 = x2 + w2
    bottom1 = y1 + h1
    bottom2 = y2 + h2

    intersection = max(0, min(right1, right2) - max(x1, x2)) * \
        max(0, min(bottom1, bottom2) - max(y1, y2))

    return intersection / (area1 + area2 - intersection)


def init_tracker(tracker_name, image, boundingBox):
    tracker_name = tracker_name.lower()
    if tracker_name == 'boosting':
        tracker = cv2.TrackerBoosting_create()
    elif tracker_name == 'goturn':
        tracker = cv2.TrackerGOTURN_create()
    elif tracker_name == 'kcf':
        tracker = cv2.TrackerKCF_create()
    elif tracker_name in ['mf', 'medianflow']:
        tracker = cv2.TrackerMedianFlow_create()
    elif tracker_name == 'mil':
        tracker = cv2.TrackerMIL_create()
    elif tracker_name == 'tld':
        tracker = cv2.TrackerTLD_create()
    elif tracker_name == 'dlib':
        tracker = dlib.correlation_tracker()
    else:
        raise Exception('No such tracker.')

    x, y, w, h = boundingBox
    if isinstance(tracker, dlib.correlation_tracker):
        tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))
    else:
        tracker.init(image, tuple(boundingBox))

    return tracker


def update_tracker(tracker, image):
    if isinstance(tracker, dlib.correlation_tracker):
        tracker.update(image)
        rect = tracker.get_position()
        boundingBox = rect.left(), rect.top(), rect.right() - \
            rect.left(), rect.bottom() - rect.top()
    else:
        _, boundingBox = tracker.update(image)

    return boundingBox


def tracks(tracker_name, images, groundtruth, reinit_acc=10, reinit_robust=5):
    if tracker_name not in ['mil', 'tld']:
        return track(tracker_name, images, groundtruth, reinit_acc, reinit_robust)

    n_tracks = 10
    acc_list = []
    fail_list = []
    for _ in range(n_tracks):
        acc, fail, box = track(tracker_name, images, groundtruth, reinit_acc, reinit_robust)
        acc_list.append(acc)
        fail_list.append(fail)

    return np.mean(acc_list, axis=0).tolist(), float(np.mean(fail_list)), box


def track(tracker_name, images, groundtruth, reinit_acc=10, reinit_robust=5):
    assert len(images) >= len(groundtruth)

    acc = [0]*(len(groundtruth) - 1)
    fail = 0
    box = []

    update_counter = 0
    fail_counter = 0

    v_h, v_w, _ = images[0].shape
    def modify(box):
        x, y, w, h = box
        x = 0 if x < 0 else x
        y = 0 if y < 0 else y
        h = v_h - y - 1 if y + h >= v_h else h
        w = v_w - x - 1 if x + w >= v_w else w
        return x, y, w, h

    for i, box_g in enumerate(groundtruth):
        image = images[i]

        box_g = modify(box_g)

        if i == 0:
            tracker = init_tracker(tracker_name, image, box_g)
            # print('Running {}...'.format(tracker.__class__))
            continue

        # update
        box_t = update_tracker(tracker, image)
        update_counter += 1

        box.append(box_t)

        # compute accuracy
        current_accuracy = accuracy(box_t, box_g)
        acc[i - 1] = current_accuracy

        # reduce bias
        if current_accuracy == 0:
            fail += 1
            fail_counter += 1

        if fail_counter == reinit_robust:
            tracker = init_tracker(tracker_name, image, box_g)
            fail_counter = 0
            update_counter = 0

        if update_counter == reinit_acc:
            tracker = init_tracker(tracker_name, image, box_g)
            update_counter = 0
            fail_counter = 0

    #     x, y, w, h = box_t
    #     cv2.rectangle(image, (int(x), int(y)), (int(x+w), int(y+h)), (255, 0, 255), 2)
    #     x, y, w, h = box_g
    #     cv2.rectangle(image, (int(x), int(y)), (int(x+w), int(y+h)), (0, 0, 0), 2)
    #     cv2.imshow('frame', image)
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
    # cv2.destroyAllWindows()
    return acc, fail, box


def track_all_videos(tracker_name, datasets):
    os.makedirs('tmp', exist_ok=True)
    pickle_filename = 'tmp/{}.pickle'.format(tracker_name)

    res = {}
    if os.path.exists(pickle_filename):
        res = pickle.load(open(pickle_filename, 'rb'))

    for video_name in datasets:
        if video_name in res:
            continue

        res[video_name] = []

        images, groundtruth_list = read_data(video_name)
        for i, groundtruth in enumerate(groundtruth_list):
            acc, fail, box = tracks(tracker_name, images, groundtruth)
            res[video_name].append({'acc': acc, 'fail': fail, 'box': box})

        pickle.dump(res, open(pickle_filename, 'wb'))


def main():
    vtb = json.load(open('datasets/vtb/vtb.json', 'r'))

    remove_list = ['David', 'Bird1']
    for r in remove_list:
        print('Remove {}'.format(vtb.pop(r, None)))

    parser = argparse.ArgumentParser()
    parser.add_argument('tracker', type=str)
    # parser.add_argument('--imshow', action="store_true")
    args = parser.parse_args()

    remove_list = ['David', 'Bird1']

    t = args.tracker
    if t:
        track_all_videos(t, vtb)

if __name__ == '__main__':
    main()
