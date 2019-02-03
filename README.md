# Yet (not) another Annotation Tool

A repository to supplement the paper "A Comparative Study of Video Annotation Tools for Scene Understanding: Yet (not) another Annotation Tool": https://doi.org/10.1145/3304109.3306223

```bash
nano
+-- acquired_data
|   +-- annotations
|   |   +-- gt
|   |   |   +-- gameplay_groundtruth.txt
|   |   |   +-- medical_groundtruth.txt
|   |   |   +-- pedestrian_groundtruth.txt
|   |   +-- users
|   |   |   +-- aibu
|   |   |   +-- darklabel
|   |   |   +-- vatic
|   +-- user_study_data.csv
+-- evaluation
|   +-- docker-source
+-- video_contents
|   +-- docker_data_vatic
|   +-- extracted_frames_aibu
|   +-- atest.mp4
|   +-- endo.mp4
|   +-- fortnite.mp4
|   +-- tud.mp4
+-- tools
|   +-- aibu-clone.zip
|   +-- darklabel1.3-release.zip
|   +-- vatic-clone.zip
+-- questionnaire
|   +-- INTERVIEW.md
|   +-- SURVEY.md
```
## Subjects
In the user study, 45 people participate and each participate tested one tool with three video contents in a mixed-design.

## Tools
Three tools are compared between subjects:

1. DarkLabel -> [Go and have a look on the website](http://darkpgmr.tistory.com/16)
2. AIBU -> [Go and have a look on GitHub](http://github.com/votchallenge/aibu)
3. VATIC (used as docker image)
  * Official cited repository [Go and have a look on GitHub](https://github.com/cvondrick/vatic)
  * Docker contribution [Go and have a look on GitHub](https://github.com/jldowns/vatic-docker-contrib) or [Go and have a look on DockerHub](https://hub.docker.com/r/jldowns/vatic-docker-contrib/)

![preview tools](/previews/tools/tools_preview.png)

In the directory ''tools'' a clone of each tool is included. AIBU, VATIC are GitHub clones. VATIC includes a clone of the cited VATIC and DOCKER-CONTRIB repository, respectively. DarkLabel includes a copy of the released tool version, available on the website.
Each tool provides an installation setup in its corresponding reposiotry. For a quick setup:
  * AIBU requires a Java Runtime + ant package manager to include the coffeeshop library in the Ivy repository and finally build the tool with ant.
  * DarkLabel requires a Windows system and the provided .dll file in the same directory.
  * VATIC can be executed with the provided docker image in the following way:

  ```bash
    # Execute VATIC-docker-contrib
    cd ./nano
    ROOT_DIR=`pwd`
    cd $ROOT_DIR/tools
    unzip -a vatic-clone.zip
    unzip -a vatic-docker-contrib-master.zip
    cd vatic-docker-contrib-master
    # specify a shared data directory
    DATA_DIR=$ROOT_DIR/video_contents/docker_data_vatic/data
    # check if everything worked
    echo $DATA_DIR
    # start docker and map shared directory
    docker run -it -p 8080:80 -v $DATA_DIR:/home/vagrant/vagrant_data jldowns/vatic-docker-contrib:0.1
    # now you are in the docker container
    # start MySQL
    root@[CONTAINER_ID]:~# /home/vagrant/start_services.sh
    # go to
    root@[CONTAINER_ID]:~# cd /home/vagrant/vatic
    # extract keyframes from a video
    root@[CONTAINER_ID]:~# turkic extract /home/vagrant/vagrant_data/atest.mp4 /home/vagrant/vagrant_data/atest_frames/
    # for mac users delete all .DS_Store files in the atest_frames directory
    root@[CONTAINER_ID]:~# find /home/vagrant/vagrant_data/atest_frames/ -name '.DS_Store' -type f -delete
    # laod the frames for an annotation task
    root@[CONTAINER_ID]:~# turkic load 1 /home/vagrant/vagrant_data/atest_frames/ person car instrument --offline
    # publish it locally with the --offline flag
    root@[CONTAINER_ID]:~# turkic publish --offline
    # opent the URL in the browser do not forget the port (8080)
    # Output -> http://localhost:8080/?id=1&hitId=offline
    # exit and close container
    root@[CONTAINER_ID]:~# exit
  ```

## Videos
Three videos are compared within subjects:
1. Medical endoscopy
2. Gameplay
3. Walking pedestrian

![preview videos](/previews/videos/videos_preview.png)

## Acquired Data
* To measure efficiency, the required time of each user for annotating a video was recorded separately. This time was then entered by the user in the questionnaire at the corresponding video.
* To measure effectiveness and accuracy of annotations, the directory ''gt'' includes a ground-truth annotation file for each video content. Each line represents the coordinates of the object (x1,y1,x2,y3) in the frame which a user had to follow during the video. The line number represents the frame number in the corresponding video.
* Each tool offers a different method for extracting users' annotations and the directory ''users'' includes the annotation files for each tool and corresponding user.

The file ''user_study_data.csv'' comprises all acquired data:
* user id #type: int
* gender #type: string(male, female)
* age #type: int
* tool #type: string(VATIC, AIBU, DarkLabel)
* {medical, gameplay, pedestrian}_iou #type: float(between 0 and 1.0)
* {medical, gameplay, pedestrian}_time #type: int(seconds)
* {medical, gameplay, pedestrian}_vLike #type: int(1,2,3,4,5)
* {medical, gameplay, pedestrian}_vEffort #type: int(1,2,3,4,5)
* {medical, gameplay, pedestrian}_vMotion #type: int(1,2,3,4,5)
* tUsage #type: int(1,2,3,4,5)
* tBoxCreation #type: int(1,2,3,4,5)
* tBoxManipulation #type: int(1,2,3,4,5)
* tBoxPropagation #type: int(1,2,3,4,5)

## Evaluation & Results
Scripts for evaluating user study data are implemented in python by utilizing several scientific packages for statistical analysis. Interactive navigation through results and source code are provided with a docker image. All source code can be found in the directory ''docker-source''. This directory is used by the docker container in order to calcuate the results. To build the docker from source enter the following statements:

```bash
  cd ./nano/evaluations/docker-source
  #Build docker image
  sh build_and_run.sh
  # type the following URL in the browser
  # -> localhost:4000

  # Stop docker container
  docker container ls
  docker stop [CONTAINER ID]

  # or to clean any dangling docker files
  sh cleanup.sh
```
Alternatively, a public available docker image can also be used:
```bash
  # Pull the image from Docker Hub
  docker pull amplejoe/nano:artifacts
  # Run the image
  docker run -p 4000:80 amplejoe/nano:artifacts
  # type the following URL in the browser
  # -> localhost:4000
```
A navigation menu provides links for reproducing all study results.
### Configuration

In general all configurations are found in ``docker-source/app/config.py``

### Generate IoU's
Calculates IoU's per user according to the ground-truth data.
* Script: ``docker-source/app/calc_iou.py``
* Input: annotation files from tools ``acquired_data/users`` and ground-truth files ``acquired_data/gt``
* Output: csv file including all IoUs per tool and video

### Results

#### Subjective Assessment
* Script: ``docker-source/app/calculate.py``
* Method: ``subjective()``
* Input: csv file as pandas dataframe
* Output: Subjectives assessments evaluated with Friedman Chi Square, Kruskal-Wallis H test and Dunn's post hoc analysis

#### Efficiency (Time)
* Script: ``docker-source/app/calculate.py``
* Method: ``efficiency()``
* Input: csv file as pandas dataframe
* Output: Assessment according to time: Shapiro Wilkinson (normality), Mixed ANOVA, Welch's test and Games-Howell post hoc analysis

#### Effectiveness (IoU)
* Script: ``docker-source/app/calculate.py``
* Method: ``effectiveness()``
* Input: csv file as pandas dataframe
* Output: Assessment according to iou: Shapiro Wilkinson (normality), Kruskal-Wallis H test, Conover-Iman test post hoc analysis

#### Correlations
* Script: ``docker-source/app/calculate.py``
* Method: ``correlations()``
* Input: csv file as pandas dataframe
* Output: Assessment according to time and iou: Spearmans Rank Correlation Coefficient

# Acknowledgements
When using study data, please cite the following paper:


> Sabrina Kletz, Andreas Leibetseder, Klaus Schoeffmann. A Comparative Study of Video Annotation Tools for Scene Understanding: Yet (not) another Annotation Tool "10th ACM Multimedia Systems Conference (MMSys)". June 2019. https://doi.org/10.1145/3304109.3306223


# Bugs
Please report errors on the issues page of this repository.
