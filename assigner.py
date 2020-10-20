import json
import jieba
import random
import plotly.express as px
import argparse
import sys

jieba.setLogLevel(20)  # disable initialization info

parser = argparse.ArgumentParser()

parser.add_argument(
    "-v",
    "--visualize",
    required=False,
    default=False,
    help="whether to visualize results",
)
parser.add_argument(
    "-l",
    "--location",
    required=False,
    default="data/known.txt",
    help="location for known user vocabulary",
)
parser.add_argument(
    "-t",
    "--typesplit",
    required=True,
    default="wo",
    help="whether to split sentences character by character (ch) or word by word (wo)",
)
parser.add_argument(
    "-s",
    "--sort",
    required=False,
    default="HSK",
    help="whether to sort sentences by 'HSK' or 'custom' (user ratio)",
)
parser.add_argument(
    "--string",
    required=False,
    default="",
    help="string used when searching sentences, split words by space",
)
parser.add_argument(
    "--smallest",
    required=False,
    default=0.6,
    help="smallest ratio of sentences known when searching (default is 0.6)",
)
parser.add_argument(
    "-e",
    "--easy",
    required=False,
    default=True,
    help="whether to output 'custom' sentences the user is most likely to understand (default True), as opposed to any sentences above the `smallest`",
)
parser.add_argument(
    "-i",
    "--include",
    required=False,
    default=True,
    help="whether to add custom sentence ratio to `data/sentences.tsv` (requires `location`, default True (with working `location`))",
)
parser.add_argument(
    "--limit", required=False, default=10, help="number of sentences outputted"
)
parser.add_argument(
    "-m",
    "--mine",
    required=False,
    default=False,
    help="whether or not to mine sentences (default is False)",
)
parser.add_argument(
    "-d",
    "--deviation",
    required=False,
    default=0.2,
    help="HSK/user ratio deviation when searching for sentences (default of 0.2 means for 3 you will find sentences from 2.8 - 3.2)",
)
parser.add_argument(
    "--target",
    required=False,
    help="target HSK level (int/float) when searching for sentences",
)
parser.add_argument(
    "-o",
    "--output",
    required=False,
    default="HSK",
    help="output type & visualization type - return HSK sentences (default of 'HSK') or custom ratio sentences ('custom'), required for visualization and sentence mining",
)

args = vars(parser.parse_args())


class SentenceAssigner:
    """
    Assigns sentences in `data/sentences.tsv` an HSK average
    and custom ratio based on known user vocabulary.
    
    Useful for finding sentences applicable at user's level.
    
    Keyword Arguments:
    `vocab_location=None` -- location for user's known vocabulary
    """

    # read HSK json as dict
    file = open("data/hsk.json", "r")
    levels = json.load(file)
    file.close()

    # build HSK database
    hsk_data = {}
    for definition in levels:
        hsk_data[definition["hanzi"]] = definition["HSK"]

    punctuation = "， 。 / ； ‘ 、 【 】 1 2 3 4 5 6 7 8 9 0 - = · § — — + 「 」 ： “ ｜ ？ 》 《 ！ @ # ¥ % & * （ ）".split()

    def __init__(self, vocab_location=None, char_by_char: bool = False):
        self.char_by_char = char_by_char

        if vocab_location is not None:
            self.known_words = open(vocab_location, "r").read().splitlines()
        else:
            self.known_words = []

        # split multi-line words into constituent parts
        if self.char_by_char is True:
            placeholder = []
            for word_str in self.known_words:
                for char in word_str:
                    placeholder.append(char)

            self.known_words = placeholder

    def rewrite_file(self):
        """
        Overwrites `sentences.tsv` with data in `self.sentences`.
        """

        # open document for writing
        with open("data/sentences.tsv", "w") as writer:
            writer.write(
                "// Characters | Pinyin | Meaning | HSK average | Custom Ratio\n"
            )  # initial line
            for line in self.sentences:

                # backslashes are banned in f-strings
                tab = "\t"
                newline = "\n"

                if self.custom == True:
                    writer.write(
                        f"{''.join(ch for ch in line[0])}{tab}{line[1]}{tab}{line[2].rstrip(newline)}{tab}{line[3]}{tab}{line[4]}{newline}"
                    )
                else:
                    writer.write(
                        f"{''.join(ch for ch in line[0])}{tab}{line[1]}{tab}{line[2].rstrip(newline)}{tab}{line[3]}{tab}{tab}{newline}"
                    )

    def known_ratio(self, jieba_str: str) -> float:
        """
        Adds ratios to `sentences.tsv` as equation
        ```python
        ratio = known / total
        ```
        """

        known_count = 0
        str_len = len(jieba_str)

        for char in jieba_str:
            if char in self.known_words:
                known_count += 1
            elif char in self.punctuation:
                str_len -= 1

        return round(known_count / str_len, 3)

    def parse_document(self, custom: bool = False):
        """
        Parses JSON document and adds HSK difficulty (optional: custom difficulty).
        """

        self.custom = custom

        with open("data/sentences.tsv", "r") as file:
            self.sentences = file.readlines()[1:]

        for i in range(len(self.sentences)):
            self.sentences[i] = self.sentences[i].split("\t")

        if self.char_by_char == False:
            self.sentences[:] = [
                [[hanzi for hanzi in jieba.cut(sentence[0])], sentence[1], sentence[2]]
                for sentence in self.sentences
            ]
        else:
            self.sentences[:] = [
                [[hanzi for hanzi in sentence[0]], sentence[1], sentence[2]]
                for sentence in self.sentences
            ]

        # calculate HSK difficulty
        for i in range(len(self.sentences)):
            self.sentences[i].append(self.calc_hsk_avg(self.sentences[i][0]))

        if self.custom == True:
            for i in range(len(self.sentences)):
                self.sentences[i].append(self.known_ratio(self.sentences[i][0]))

    def calc_hsk_avg(self, jieba_str: str) -> float:
        """
        Calculates difficulty of Chinese string by finding the average of word levels.

        Note: inaccurate with `char_by_char` set to True.
        """

        hsk_total = 0
        str_len = len(jieba_str)

        for char in jieba_str:

            if char in self.hsk_data:
                hsk_total += self.hsk_data[char]
            elif char in self.punctuation:
                str_len -= 1  # everyone knows punctuation
            else:
                hsk_total += 7

        return round(hsk_total / str_len, 3)

    def sort_file(self, key: str = "HSK"):
        """
        Sort sentences in list via "HSK" or "custom"
        """

        if key == "HSK":
            self.sentences = sorted(self.sentences, key=lambda x: x[3])
        elif key == "custom":
            self.sentences = reversed(sorted(self.sentences, key=lambda x: x[4]))
        else:
            print("Please provide a valid sorting method!")

        self.rewrite_file()


class DataVisualizer:
    """
    Visualizes the sentences in `data/sentences.tsv` based on rules as line chart.
    """

    def __init__(self, key):
        self.key = key

        if self.key == "HSK":
            with open("data/sentences.tsv", "r") as file:
                self.data = file.read().splitlines()[1:]

                placeholder = []
                for i in range(len(self.data)):
                    self.data[i] = self.data[i].split("\t")
                    if float(self.data[i][3]) not in placeholder:
                        placeholder.append(float(self.data[i][3]))

                intermediary_data = []
                for i in range(len(self.data)):
                    intermediary_data.append(float(self.data[i][3]))

                self.counter = []

                for ele in placeholder:
                    self.counter.append(intermediary_data.count(ele))

                self.data = placeholder

        elif self.key == "custom":
            with open("data/sentences.tsv", "r") as file:
                self.data = file.read().splitlines()[1:]

                placeholder = []
                for i in range(len(self.data)):
                    self.data[i] = self.data[i].split("\t")
                    if float(self.data[i][4]) not in placeholder:
                        placeholder.append(float(self.data[i][4]))

                intermediary_data = []
                for i in range(len(self.data)):
                    intermediary_data.append(float(self.data[i][4]))

                self.counter = []

                for ele in placeholder:
                    self.counter.append(intermediary_data.count(ele))

                self.data = placeholder

    def visualize(self):
        """
        Performs visualization operation, outputting to browser.
        """
        zipped_lists = zip(self.data, self.counter)
        sorted_zipped_lists = sorted(zipped_lists)

        self.data = [element for element, _ in sorted_zipped_lists]
        self.counter = [element for _, element in sorted_zipped_lists]
        fig = px.line(x=self.data, y=self.counter)
        fig.show()


def best_sentences(
    search_str: str = "", minimum: float = 0.5, limit: int = 10, highest: bool = True
) -> list:
    """
    Finds the sentences the user will be most likely to understand when given an input string.

    Keyword arguments:
    `search_str` (default "") -- search for sentences only with this character/characters (separated by space)

    `minimum` (default 0.0) -- how much of the words in a sentence the user understands

    `limit` (default 20) -- maximum number of sentences returned in the function

    `highest` (default True) -- whether to return only the most understood sentences or any sentences (up to limit) above `minimum`
    """
    sentences = []
    with open("data/sentences.tsv", "r") as file:
        for line in file.read().splitlines()[1:]:
            line = line.split("\t")
            in_line = True
            for char in search_str.split(" "):
                if char not in line[0]:
                    in_line = False

            if in_line == True:
                if float(line[4]) >= minimum:
                    sentences.append((line[0], line[1], line[2], line[4]))

    if highest == True:
        sentences.sort(key=lambda x: x[3])
        sentences = list(reversed(sentences))
    else:
        random.shuffle(sentences)

    return sentences[:limit]


def hsk_grabber(
    target_hsk: float, search_str: str = "", deviation: float = 0.2, limit: int = 10
):
    """
    Finds HSK sentences at `target_hsk` level, with a ± deviation of `deviation`.

    Search for sentences that contain words (space-separated) with `search_str` and set a sentence output limit with `limit`.
    """
    sentences = []
    with open("data/sentences.tsv", "r") as file:
        for line in file.read().splitlines()[1:]:
            line = line.split("\t")
            in_line = True
            for char in search_str.split(" "):
                if char not in line[0]:
                    in_line = False

            if in_line == True:
                if (
                    float(line[3]) < target_hsk + deviation
                    and float(line[3]) > target_hsk - deviation
                ):
                    sentences.append((line[0], line[1], line[2], line[3]))

    random.shuffle(sentences)

    return sentences[:limit]


# run file based on user input
if "location" in args.keys():
    try:
        file = open(args["location"], "r")
        file.close()
        if args["typesplit"] == "ch":
            manager = SentenceAssigner(args["location"], True)
        else:
            manager = SentenceAssigner(args["location"])
    except:
        manager = None
        print("Please provide a valid known words file!")
        sys.exit()

else:
    if args["typesplit"] == "ch":
        manager = SentenceAssigner(args["location"], True)
    else:
        manager = SentenceAssigner(args["location"])

if bool(args["include"]) == False:
    manager.parse_document()
else:
    manager.parse_document(custom=True)


if args["sort"] == "custom":
    manager.sort_file(key="custom")
else:
    manager.sort_file()

if bool(args["visualize"]) == True:
    if args["output"] == "custom":
        visualizer = DataVisualizer(key="custom")
    else:
        visualizer = DataVisualizer(key="HSK")

    visualizer.visualize()

if bool(args["mine"]) == True:
    if args["output"] == "custom":
        ordered_sentences = best_sentences(
            args["string"],
            minimum=float(args["smallest"]),
            limit=int(args["limit"]),
            highest=bool(args["easy"]),
        )

        for sentence in ordered_sentences:
            print(sentence, "\n")

    elif args["output"] == "HSK":
        if args["target"] is None:
            hsk_sentences = hsk_grabber(
                3.5,
                search_str=args["string"],
                deviation=3.5,  # any HSK sentences
                limit=int(args["limit"]),
            )
        else:
            hsk_sentences = hsk_grabber(
                float(args["target"]),
                search_str=args["string"],
                deviation=float(args["deviation"]),
                limit=int(args["limit"]),
            )

        for sentence in hsk_sentences:
            print(sentence, "\n")

