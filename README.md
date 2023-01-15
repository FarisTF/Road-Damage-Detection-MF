# Pipeline Road Damage Detection - Matching Fund

## Cara menjalankan
1. Setup dulu CUDA Toolkit sama CUDNN yang versinya support tensorflow-gpu versi 2.7.0  
https://www.tensorflow.org/install/source#gpu (di bagian tested build configuration)

2. Buka main.ipynb

3. jika baru pertama kali, jalanin cell paling bawah yang isinya:
```
!pip install -r requirements.txt
```
  (tensorflow-gpu yang bakal diinstall 2.7.0 jadi hati hati kedowngrade)
  
4. Jalanin cell paling atas yang isinya:
```
from pipeline_func import *
```

5. Ubah-ubah input_video dengan path video input yang diinginkan, dan ubah out_folder dengan nama folder keluaran yang diinginkan
```
print("Start") # Biar bisa keliatan progressnya (kalo dijalanin di vscode)

input_video = "input/1.mp4"
out_folder = "video_itebe"

# Definisi fungsi ada file pipeline_func.py di definisi fungsi terakhir (line 498)
road_damage_detection(input_video, out_folder)
```
6. Tunggu 👍

## Deteksi Lubang
<p align="center"><img src="dependency/gif/Lubang.gif"\></p>

## Deteksi Retak Kulit Buaya
<p align="center"><img src="dependency/gif/Retak_Kulit_Buaya.gif"\></p>
