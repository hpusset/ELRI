# ELRI National Relay Station (forked from the ELRC-SHARE SOFTWARE)

`ELRC-SHARE SOFTWARE` project: [https://github.com/JuliBakagianni/CEF-ELRC](https://github.com/JuliBakagianni/CEF-ELRC)

`ELDA` webapp project: (https://github.com/ELDAELRA/ELRI)[https://github.com/ELDAELRA/ELRI]


## Pull last changes from ELDA

To pull last changes it is necessary to add `ELDA` webapp repository as a new remote repository. Then all changes can be pulled or pushed to any repository.

1. Clone this repository:
```
git clone git@gitlab.vicomtech.es:ELRI_EU2377_2016/ELRI.git
```
2. Add `ELDA` webapp project `URL` as remote:
```
git remote add elda https://github.com/ELDAELRA/ELRI.git
```
3. Pull last changes:
```
git pull elda master
```
4. Push last changes to `GitLab`:
```
git add .
git commit -m "some commentary"
git pull origin master
```
