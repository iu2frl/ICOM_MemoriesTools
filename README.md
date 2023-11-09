# ICOM Memories tool

## Introduction

I have a lot of ICOM radios, but i really hate the fact that every device has a different memory file which is incompatible with the others.

## Purpose of this project

As the `ICF` files are just big chunks of HEX data, i thougt to reverse engineer them in order to export its content to a standard `CSV` file ([Chirp](https://chirp.danplanet.com/projects/chirp/wiki/Home) compatible) and then convert such `CSV` back to any different radio model (which is still an `ICF` format). This way i can create a memory file for an __IC-2820__ and make it compatible with an __ID-5100__

## Current status

I started with the two devices I use the most

### ICOM IC-2820

#### ICF to CSV

Reading the memory file was relatively easy as I have a big amount of `ICF` files that i can process. I am now able to read a memory file and export it to a Chirp-compatible `CSV`

#### CSV to ICF

Not started yet

### ICOM ID-51 Plus

#### ICF to CSV

I started with some testing but there's still a lot of work to do

#### CSV to ICF

Not started yet
