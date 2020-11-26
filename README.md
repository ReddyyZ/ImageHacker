<h1 align="center">ImageHacker</h1>
<p align="center">Tool for extract and edit exif image data! Developed in Python3 using <b>Pillow</b> and <b>piexif</b> libs.</p>
<p align="center"></p>

## How to install
- Clone the repo
```bash
git clone https://github.com/ReddyyZ/ImageHacker
```

- Install 
```bash
python3 install.py
```

- Try on!
```bash
imagehacker --extract example.jpg
```

## How to use
- Extracting exif image data
```bash
imagehacker --extract <IMAGE FILE>
```

- Change GPS data
```bash
imagehacker --insert --gps "37.090240 -95.712891 800" <IMAGE FILE>
```

- Change date
```bash
imagehacker --insert --date "2020:11:25 14:31:21" <IMAGE FILE>
```

## Images samples
If you want to try the script, clone the [exif-samples repo](https://github.com/ianare/exif-samples).

---

<h2 align="center">&lt;/&gt; by <a href="https://github.com/ReddyyZ">ReddyyZ</a></h2>