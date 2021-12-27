# Code by Heart API

## Spaced Repetition Algorithm 

-This program uses SM-2: a simple spaced repetition algorithm that 
calculates the number of days to wait before reviewing a piece of 
information based on how easily the information was remembered today.
-More info here: https://www.supermemo.com/en

-The algorithm requires four inputs: quality (an integer from 0-5 indicating how easily the information was remembered by the user -- this could correspond to a button such as "Difficult" or "Very Easy."), repetitions, previous ease factor, and previous interval. The last three inputs are taken from the output of a previous call to SM-2. (On the first call, default values are used.)

-Detailed info here: https://github.com/thyagoluciano/sm2

