# Chinese Sentence Miner
Filter and sort over 18,000 Simplified Chinese sentences to find those just right for you!

This program is perfect for finding new sentences that you'll be able to understand (e.g., for flashcards, rote learning), as well as visualizing your comprehension of Chinese texts using Matplotlib.

![](images/sample.png "program generating sentences")

## Features
*By adding a `.txt` document with your known vocabulary (such as `data/known.txt`), you can use the program to assign each sentence a 'custom ratio' - your known words divided by total words.*

- Assign custom ratios to sentences based on your known vocabulary
- Access sentences through various filtering methods, such as by:
    - Searching for specific word(s) in sentences
    - Searching for sentences within an HSK or custom ratio range
    - Defining the maximum number of sentences you'll get
    - Specifying the minimum understanding of a sentence required
- Visually graph your understanding of sentences using Matplotlib
- Add and analyze your own sentences to the database
- Sort sentences based on their average HSK level or your custom ratio

## High-level Overview
The program is CLI-only and contains approximately 18k sentences of varying difficulty stored in `data/sentences.tsv`, taken from Tatoeba. It allows you to search through these sentences using a simple set of rules - see **Usage**. While sentences can be searched for based on their HSK difficulty, the tool is most useful when you want to find sentences that *suit your level*.

The `data/known.txt` file contains carriage-separated words that you know - currently holding an example of several hundred. By filling in this file, you can then filter sentences according to your understanding of them.

## Usage

**For those unfamiliar with coding, the code can also be run online:**
[Run online](https://repl.it/@andersoncliffb/chinese-sentence-miner#README.md).

Make sure to check out the [examples](#examples) section to understand how to run the code.

*Usage with Anki: create a field named `Sentences` for the card template you are using with Chinese words. Create a sorted `sentences.tsv` file based on (ideally) 'custom' understanding. Steadily cmd-f your way through each word in your Anki deck/use the CLI.*

*Note: you can also try exporting Anki decks as a txt file, modifying them, and then re-importing them. Note that with CLI and depending on deck size, this may take some time.*

### Installation
1. Download this repository by clicking the green `code` button at the top right.
2. Navigate to the folder with the program in your Terminal.
3. Install Python requirements with `python3 -m pip install -r requirements.txt`.
4. Run `python3 assigner.py` with your [desired flags](#flags).

*Note: Parsing nearly 20,000 sentences takes time. Commands typically execute in 15-25 seconds.*

### Flags
`chinese-sentence-miner` has many flags for filtering or visualizing sentences. Type `python3 assigner.py --help` for flag descriptions, or consult this guide.

```
usage: assigner.py [-h] [-v] [-l LOCATION] [-t {ch,wo}] [-s {HSK,custom}] [--string STRING] [--smallest SMALLEST] [-e] [-i] [--limit LIMIT] [-m] [-d DEVIATION] [--target TARGET] [-o {HSK,custom}]

options:
  -h, --help            show this help message and exit
  -v, --visualize       whether to visualize results
  -l LOCATION, --location LOCATION
                        location for known user vocabulary
  -t {ch,wo}, --typesplit {ch,wo}
                        split sentences character by character (ch) or word by word (wo)
  -s {HSK,custom}, --sort {HSK,custom}
                        sort sentences by 'HSK' or 'custom' (user ratio)
  --string STRING       string used when searching sentences, split words by space
  --smallest SMALLEST   smallest ratio of sentences known when searching (default is 0.6)
  -e, --easy            output 'custom' sentences the user is most likely to understand (default True)
  -i, --include         add custom sentence ratio to `data/sentences.tsv`
  --limit LIMIT         number of sentences outputted
  -m, --mine            whether or not to mine sentences
  -d DEVIATION, --deviation DEVIATION
                        HSK/user ratio deviation when searching for sentences
  --target TARGET       target HSK level when searching for sentences
  -o {HSK,custom}, --output {HSK,custom}
                        output type & visualization type
```

#### location
*Flags: `-l`, `--location`*

Specifies the location of your known vocabulary. Example: `python3 assigner.py --location "data/known.txt"`. Required for sorting by custom ratio, visualizing custom ratio, and outputting sentences based on custom ratio.

#### output
*Flags: `-o`, `--output`*

**Important flag!**

Specifies whether to use `"HSK"` or `"custom"` (for custom ratios) when searching for sentences.

#### mine
*Flags: `-m`, `--mine`*

Enables sentence output. Set it have sentences printed. Example: `python3 assigner.py --mine`.

#### visualize
*Flags: `-v`, `--visualize`*

Controls whether a visualization of the sentences is outputted. The visualization is a bar chart displaying your understanding of each sentence, *or* the HSK level of each sentence (based on the [output flag](#output)).

Set to `False` by default. Enable with `python3 assigner.py --visualize`.

#### typesplit
*Flags: `-t`, `--typesplit`*

Choose how sentences are split: `"wo"` (word by word, default) or `"ch"` (character by character). Character splitting is useful for more granular understanding.

#### sort
*Flags: `-s`, `--sort`*

Determines how `data/sentences.tsv` is sorted. `"HSK"` orders sentences from lowest to highest HSK level. `"custom"` orders them from most to least understandable.

#### include
*Flags: `-i`, `--include`*

Rewrites `sentences.tsv` with the HSK ratio. Enables adding custom ratios. Recommended to keep enabled.

#### string
*Flag: `--string`*

Used for sentence output. Allows specifying a string, and only sentences containing it will be outputted.

#### limit
*Flag: `--limit`*

Sets the maximum number of sentences outputted. Default is 10.

#### deviation
*Flags: `-d`, `--deviation`*

Specifies the deviation when searching for HSK/custom ratio sentences. For example, a target HSK of 3.5 with a deviation of 0.2 searches for sentences from 3.3 to 3.7.

#### smallest
*Flag: `--smallest`*

Specifies the minimum understanding required when searching for sentences.

#### easy
*Flags: `-e`, `--easy`*

Determines whether to show only the easiest sentences when outputting.

#### target
*Flag: `--target`*

Specifies the target HSK level when searching for HSK sentences.

### Examples
*See examples section for various usage scenarios.*

## Contributing

### Sentences
Add sentences to `data/sentences.tsv` in the following format:
```
<sentence in Simplified characters><tab><sentence in pinyin><tab><meaning in English>
```

### Code
Code contributions are welcome! Potential improvements include:

- [ ] Cleaner visualization of sentence distribution
- [ ] Support for numbers when splitting with `jieba`
- [ ] Implement searching for target custom ratio
- [ ] `deviation` flag support for custom ratios

## Credit
`hsk.json` uses data from [hsk-vocabulary](https://github.com/clem109/hsk-vocabulary) (MIT-licensed).

Sentences from [Pleco Forums](https://www.plecoforums.com/threads/18-896-hsk-sentences.5615/) and Tatoeba.
