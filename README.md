# RealSense-Based Data Collection for Underwater Experiments

This repository contains the source code required to collect data using an **Intel RealSense camera**, along with the **associated datasets acquired from controlled water tank experiments**. The data and tools provided here are intended to support research and development in underwater sensing, imaging, and experimental validation.

## Overview

Underwater environments introduce challenges such as light attenuation, turbidity, and noise, which significantly affect sensor performance. To study these effects in a controlled setting, data were collected using a RealSense camera deployed in a water tank under various experimental conditions.

This repository provides:
- Script for RealSense data acquisition
- Sample datasets collected in water tank experiments
- Supporting tools for data handling and visualisation

## Hardware Requirements
- Intel RealSense camera (e.g. D435 / D455)
- Water tank suitable for controlled underwater experiments
- Host machine with USB 3.0 support

## Software Requirements
- Python 3.x  
- Intel RealSense SDK (`pyrealsense2`)
- OpenCV
- NumPy
- Matplotlib (optional, for visualisation)

> Additional dependencies are listed in `requirements.txt` (if provided).

## Repository Structure
```text
├── src/                # Data acquisition and processing scripts
├── data/               # Collected water tank datasets
└── README.md
```

## Citation

If you find this repository useful in your research, please consider citing one or more of the following publications:

```bibtex
@inproceedings{tolie2024enhancing,
  title     = {Enhancing Underwater Situational Awareness: RealSense Camera Integration with Deep Learning for Improved Depth Perception and Distance Measurement},
  author    = {Tolie, Hamidreza Farhadi and Ren, Jinchang and Hasan, Md Junayed and Kannan, Somasundar},
  booktitle = {Artificial Intelligence for Security and Defence Applications II},
  volume    = {13206},
  pages     = {34--42},
  year      = {2024},
  publisher = {SPIE}
}

@article{farhadi2024effective,
  title   = {Effective Marine Monitoring with Multimodal Sensing and Improved Underwater Robotic Perception towards Environmental Protection and Smart Energy Transition},
  author  = {Farhadi Tolie, Hamidreza and Ren, Jinchang and Hasan, Md Junayed and Ma, Ping and Kannan, Somasundar and Li, Yinhe},
  journal = {Journal of Geodesy \& Geoinformation Science},
  volume  = {7},
  number  = {4},
  year    = {2024}
}
```
---

## 💬 Feedback & Contact

For questions, collaborations or feedback:

📧 **hamidreza.farhadi-tolie@warwick.ac.uk**  
📧 **h.farhaditolie@gmail.com**
