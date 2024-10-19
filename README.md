# Cov-Distance

[![Social distancing image from Freepik](assets/cover.jpg "Social distancing image from Freepik")](https://www.freepik.es/vector-gratis/medida-proteccion-distanciamiento-social_7534262.htm#page=4&query=social%20distancing&position=27&from_view=search&track=ais)

An application to measure and control the distance between pedestrians.

## Technical specifications
+ Python
+ OpenCV
+ Flask
+ Google Cloud Vision  
+ Google Cloud Videointelligence
+ Google Cloud Storage


## Motivation

During the coronavirus outbreak, I participated in a hackathon with three university colleagues as part of the Multimedia Systems course. Our project involved developing a solution using Google Cloud technologies to measure the distance between pedestrians in images. The primary objective of our application was to detect whether people were maintaining the minimum safe distance during the pandemic.

By leveraging the Google Cloud Platform, we built an innovative solution aimed at promoting public safety during the pandemic. Our application provided a fast and efficient way to assess if individuals were following social distancing guidelines.

## Description

In this project, we combined Google Cloud Platform technologies with Artificial Intelligence and Computer Vision to detect people, determine their locations, and calculate the distances between them.

Pedestrian detection was achieved by extracting frames from a video stored in Cloud Storage using OpenCV. We then employed the Vision API, specifically the `object_localization()` function, to locate objects classified as `Person`.

Finally, we implemented a Flask web application using Compute Engine to display the results of the analysis.

![alt text](https://raw.githubusercontent.com/XCoret/cov-distance/master/cov_archictecture.png)

After detecting each person's position in the frame, we calculated the distances between them using the Homography technique. This allowed us to create a mapping of the street's perpendicular view, ensuring accurate distance measurement within the image.

![alt text](https://raw.githubusercontent.com/XCoret/cov-distance/master/homografia.png)

Once the distances were computed, we applied a color-coding system for visual feedback: distances under 1.5 meters were marked in red (alert), distances between 1.5 and 2 meters in orange (precaution), and distances of 2 meters or more in green (safe).

![alt text](https://raw.githubusercontent.com/XCoret/cov-distance/master/output.png)

## Results

YouTube video
[![IMAGE ALT TEXT](https://i.ytimg.com/vi_webp/kq2AIcvd-cQ/maxresdefault.webp)](http://www.youtube.com/watch?v=kq2AIcvd-cQ "Video Title")
