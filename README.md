# Object Tracking Benchmark
## Result
### Overall
dlib > mf > boosting > mil > kcf > goturn > tld
![png](fig/Overall_acc.png)
goturn < boosting < dlib < mil < mf < tld < kcf
![png](fig/Overall_fail.png)
### IV
Illumination Variation - the illumination in the target region is significantly changed.

dlib > mf > boosting > mil > kcf > goturn > tld
![png](fig/IV_acc.png)
goturn < boosting < dlib < mil < mf < tld < kcf
![png](fig/IV_fail.png)
### SV
Scale Variation – the ratio of the bounding boxes of the first frame and the current frame is out of 

dlib > mf > boosting > mil > kcf > goturn > tld
![png](fig/SV_acc.png)
goturn < boosting < dlib < mil < mf < tld < kcf
![png](fig/SV_fail.png)
### OCC
Occlusion – the target is partially or fully occluded.

dlib > mf > boosting > mil > kcf > goturn > tld
![png](fig/OCC_acc.png)
goturn < boosting < dlib < mil < mf < tld < kcf
![png](fig/OCC_fail.png)
### DEF
Deformation – non-rigid object deformation.

dlib > mf > boosting > mil > kcf > goturn > tld
![png](fig/DEF_acc.png)
goturn < boosting < dlib < mil < mf < tld < kcf
![png](fig/DEF_fail.png)
### MB
Motion Blur – the target region is blurred due to the motion of target or camera.

dlib > mf > boosting > mil > kcf > goturn > tld
![png](fig/MB_acc.png)
goturn < boosting < dlib < mil < mf < tld < kcf
![png](fig/MB_fail.png)
### FM
Fast Motion – the motion of the ground truth is larger than tm pixels (tm=20).

dlib > mf > boosting > mil > kcf > goturn > tld
![png](fig/FM_acc.png)
goturn < boosting < dlib < mil < mf < tld < kcf
![png](fig/FM_fail.png)
### IPR
In-Plane Rotation – the target rotates in the image plane.

dlib > mf > boosting > mil > kcf > goturn > tld
![png](fig/IPR_acc.png)
goturn < boosting < dlib < mil < mf < tld < kcf
![png](fig/IPR_fail.png)
### OPR
Out-of-Plane Rotation – the target rotates out of the image plane.

dlib > mf > boosting > mil > kcf > goturn > tld
![png](fig/OPR_acc.png)
goturn < boosting < dlib < mil < mf < tld < kcf
![png](fig/OPR_fail.png)
### OV
Out-of-View – some portion of the target leaves the view.

dlib > mf > boosting > mil > kcf > goturn > tld
![png](fig/OV_acc.png)
goturn < boosting < dlib < mil < mf < tld < kcf
![png](fig/OV_fail.png)
### BC
Background Clutters – the background near the target has the similar color or texture as the target.

dlib > mf > boosting > mil > kcf > goturn > tld
![png](fig/BC_acc.png)
goturn < boosting < dlib < mil < mf < tld < kcf
![png](fig/BC_fail.png)
### LR
Low Resolution – the number of pixels inside the ground-truth bounding box is less than tr (tr =400).

dlib > mf > boosting > mil > kcf > goturn > tld
![png](fig/LR_acc.png)
goturn < boosting < dlib < mil < mf < tld < kcf
![png](fig/LR_fail.png)
