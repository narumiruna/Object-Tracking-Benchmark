import json
import pickle

import numpy as np
import os

import matplotlib.pyplot as plt

description = {
    'IV': 'Illumination Variation - the illumination in the target region is significantly changed.',
    'SV': 'Scale Variation – the ratio of the bounding boxes of the first frame and the current frame is out of the range ts, ts > 1 (ts=2).',
    'OCC': 'Occlusion – the target is partially or fully occluded.',
    'DEF': 'Deformation – non-rigid object deformation.',
    'MB': 'Motion Blur – the target region is blurred due to the motion of target or camera.',
    'FM': 'Fast Motion – the motion of the ground truth is larger than tm pixels (tm=20).',
    'IPR': 'In-Plane Rotation – the target rotates in the image plane.',
    'OPR': 'Out-of-Plane Rotation – the target rotates out of the image plane.',
    'OV': 'Out-of-View – some portion of the target leaves the view.',
    'BC': 'Background Clutters – the background near the target has the similar color or texture as the target.',
    'LR': 'Low Resolution – the number of pixels inside the ground-truth bounding box is less than tr (tr =400).'
}

tracker_names = ['boosting', 'goturn', 'kcf', 'mf', 'mil', 'tld', 'dlib']


def get_result(tracker_name):
    tracker_name = tracker_name.lower()
    res = pickle.load(open('tmp/{}.pickle'.format(tracker_name), 'rb'))
    return res


def gen_all_readme():
    readme = '# Object Tracking Benchmark\n## Result\n'

    tags = [None] + list(description.keys())
    for t in tags:
        readme = gen_readme(readme, t)
    return readme


def gen_readme(readme, tag=None, fig_format='png', fig_dpi=200):

    if tag:
        readme += '### {}\n{}\n\n'.format(tag, description[tag])
    else:
        readme += '### Overall\n'

    os.makedirs('fig', exist_ok=True)

    vtb = json.load(open('datasets/vtb/vtb.json', 'r'))
    if tag:
        new_vtb = {}
        for v_name in vtb:
            tags = vtb[v_name]['tags']
            if tag in tags:
                new_vtb[v_name] = vtb[v_name]
        vtb = new_vtb

    acc_data = []
    fail_data = []

    acc_labels = []
    fail_labels = []

    acc_pair = []
    fail_pair = []

    for tracker_name in tracker_names:
        res = get_result(tracker_name)
        acc_list = []
        fail_list = []
        for v_name in res:
            for obj in res[v_name]:
                acc_list.append(obj['acc'])
                fail_list.append(obj['fail'])

        acc_array = np.concatenate(acc_list)

        avg_acc = np.mean(acc_array)
        avg_fail = np.mean(fail_list)

        acc_labels.append('%s\n%.3f\n' % (tracker_name, avg_acc))
        fail_labels.append('%s\n%1.3f' % (tracker_name, avg_fail))

        acc_pair.append([avg_acc, tracker_name])
        fail_pair.append([avg_fail, tracker_name])

        acc_data.append(acc_array)
        fail_data.append(fail_list)

    tag = tag if tag else 'Overall'

    fig = plt.figure()
    fig.suptitle('{} accuracy'.format(tag))
    acc_ax = fig.add_subplot(111)
    acc_ax.boxplot(acc_data, labels=acc_labels, showfliers=False)
    acc_fig = 'fig/{}_acc.{}'.format(tag, fig_format)
    fig.savefig(acc_fig, format=fig_format, dpi=fig_dpi)

    fig = plt.figure()
    fig.suptitle('{} fail'.format(tag))
    fail_ax = fig.add_subplot(111)
    fail_ax.boxplot(fail_data, labels=fail_labels, showfliers=False)
    fail_fig = 'fig/{}_fail.{}'.format(tag, fig_format)
    fig.savefig(fail_fig, format=fig_format, dpi=fig_dpi)

    readme += ' > '.join([n for _, n in reversed(sorted(acc_pair))]) + '\n'
    readme += '![png]({})\n'.format(acc_fig)

    readme += ' < '.join([n for _, n in sorted(fail_pair)]) + '\n'
    readme += '![png]({})\n'.format(fail_fig)
    return readme

if __name__ == '__main__':
    readme = gen_all_readme()

    with open('README.md', 'w', encoding='utf8') as f:
        f.write(readme)
