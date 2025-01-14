# A MESSI system analyzer

[![Build Status](https://travis-ci.com/billy-mosse/MESSI.png)](https://travis-ci.com/billy-mosse/MESSI)

A simple program that analyzes MESSI systems and decides whether they are monostationary or multistationary. If the system is multistationary, it provides rate constants and two different steady states (on the same stoichiometric compatibility class) that witness multistationarity. The program is based on Theorem 5.4 of the article "The Structure of MESSI Biological Systems", by Alicia Dickenstein and Mercedes Pérez Millán [[arXiv](http://arxiv.org/pdf/1612.08763.pdf)][[Journal](http://www.siam.org/journals/siads/17-2/M111372.html)]. (Under construction.)

## What is it useful for?

Under development. [Visualization of (hoping: big) networks, analysis of multistationarity. It doesn't clean the dishes though.]

<!-- This program does amazing stuff -->

## Installation

Under development. When the project is finished, an executable file will be released for each major platform:
 - Windows (32 and 64 bit)
 - Linux (32 and 64 bit)
 - Mac OS X (32 and 64 bit)

## Example usage (it's really easy!):

Under development. The program will have a `--help` command and example networks to play with!

### How to analyze a custom network

Under development.

#### But, is my system MESSI?

Under development. You may check the conditions manually in [the paper](https://arxiv.org/abs/1612.08763), for now.

### Examples (built-in MESSI networks)

 <img width=70% height=70% alt="Example built with the programt" src="https://github.com/billy-mosse/MESSI/blob/master/code/phosphorylation_cascade_circo.png">

Under development

### How to test the project

Assuming you have python 3 installed, just run `python tests.py`.

Current (passing) tests:

- test_buildup_of_conformal_circuit_to_matrix

Asserts that we can correctly build a circuit conformal to a given matrix.

- test_buildup_of_incidence_matrix_from_network

Asserts that we can correctly build the incidence matrix from a given (MESSINetwork) network.

- test_buildup_of_complexes_matrix_from_network

Asserts that we can correctly build the educt complexes matrix from a given (MESSINetwork) network.

- test_buildup_of_stoichiometric_matrix_from_network

Asserts that we can correctly build the stoichiometric matrix from a given (MESSINetwork) network.

If the README has build/passing, everything's OK! It means that the tests aren't failing.

<!-- ##### How to process a big network -->

<!-- Hello! I'm a comment. I won't appear in the README file in github. In this section we have to write something like "just run python3 main.py and amazing stuff will happen"-->


<!-- Cheatsheet: https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet -->
