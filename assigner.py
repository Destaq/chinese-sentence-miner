import json
import jieba
import random
import argparse
import sys
import matplotlib.pyplot as plt
import numpy as np

# Constants
LOG_LEVEL = 20
HSK_FILE_PATH = "data/hsk.json"
SENTENCES_FILE_PATH = "data/sentences.tsv"
PUNCTUATION_SET = set("，。/；‘、【】1234567890-=·§——+「」：“｜？》《！@#¥%&*（）")
DEFAULT_KNOWN_VOCAB_LOCATION = "data/known.txt"
DEFAULT_TARGET_HSK = 3.5
DEFAULT_DEVIATION = 0.2
DEFAULT_MINIMUM_RATIO = 0.6
DEFAULT_LIMIT = 10

# Set log level for jieba
jieba.setLogLevel(LOG_LEVEL)

class SentenceAssigner:
    def __init__(self, vocab_location=None, char_by_char=False):
        self.char_by_char = char_by_char
        self.vocab_location = vocab_location or DEFAULT_KNOWN_VOCAB_LOCATION
        self._known_words = None
        self._hsk_data = None
        self._punctuation = PUNCTUATION_SET
        self.sentences = []
        self.custom = False

    @property
    def known_words(self):
        if self._known_words is None:
            self._known_words = self.load_vocab(self.vocab_location)
        return self._known_words

    @property
    def hsk_data(self):
        if self._hsk_data is None:
            self._hsk_data = self.load_hsk_data()
        return self._hsk_data

    def load_vocab(self, location):
        try:
            with open(location, "r", encoding="utf-8") as file:
                vocab = file.read().splitlines()
            return {char for word in vocab for char in word} if self.char_by_char else set(vocab)
        except IOError as e:
            print(f"Error reading vocabulary file: {e}")
            return set()

    def load_hsk_data(self):
        try:
            with open(HSK_FILE_PATH, "r", encoding="utf-8") as file:
                levels = json.load(file)
            return {definition["hanzi"]: definition["HSK"] for definition in levels}
        except IOError as e:
            print(f"Error reading HSK data file: {e}")
            return {}

    def parse_document(self, custom=False):
        self.custom = custom
        try:
            with open(SENTENCES_FILE_PATH, "r", encoding="utf-8") as file:
                raw_sentences = file.readlines()[1:]
            self.sentences = [self.process_sentence(line.split("\t")) for line in raw_sentences]
        except IOError as e:
            print(f"Error reading sentences file: {e}")

    def process_sentence(self, sentence):
        words = list(jieba.cut(sentence[0])) if not self.char_by_char else list(sentence[0])
        hsk_avg = self.calc_hsk_avg(words)
        known_ratio = self.known_ratio(words) if self.custom else None
        return [words, sentence[1], sentence[2].strip(), hsk_avg, known_ratio]

    def calc_hsk_avg(self, words):
        total, count = 0, 0
        for word in words:
            if word in self.hsk_data:
                total += self.hsk_data[word]
            elif word not in self._punctuation:
                total += 7
            count += 1 if word not in self._punctuation else 0
        return round(total / count, 3) if count else 0

    def known_ratio(self, words):
        total_count = len(words) - sum(1 for word in words if word in self._punctuation)
        known_count = sum(word in self.known_words for word in words if word not in self._punctuation)
        return round(known_count / total_count, 3) if total_count else 0

    def sort_file(self, key="HSK"):
        if key in ["HSK", "custom"]:
            reverse = key == "custom"
            self.sentences.sort(key=lambda x: x[3 if key == "HSK" else 4], reverse=reverse)
            self.rewrite_file()
        else:
            print("Invalid sorting method.")

    def rewrite_file(self):
        header = "// Characters | Pinyin | Meaning | HSK average | Custom Ratio\n"
        lines = (f"{''.join(line[0])}\t{line[1]}\t{line[2]}\t{line[3]}\t{line[4] if self.custom else ''}\n" for line in self.sentences)
        try:
            with open(SENTENCES_FILE_PATH, "w", encoding="utf-8") as writer:
                writer.write(header)
                writer.writelines(lines)
        except IOError as e:
            print(f"Error writing to sentences file: {e}")

class DataVisualizer:
    def __init__(self, file_path=SENTENCES_FILE_PATH, key="HSK"):
        self.file_path = file_path
        self.key = key
        self.data, self.counter = self.load_and_process_data()

    def load_and_process_data(self):
        index = 3 if self.key == "HSK" else 4
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                lines = file.read().splitlines()[1:]

            values = [float(line.split("\t")[index]) for line in lines if line.split("\t")[index]]
            unique_values, counts = np.unique(values, return_counts=True)

            return unique_values, counts
        except IOError as e:
            print(f"Error reading visualization data file: {e}")
            return np.array([]), np.array([])

    def visualize(self):
        if len(self.data) == 0 or len(self.counter) == 0:
            print("No data available to visualize.")
            return
    
        plt.figure(figsize=(10, 6))
        plt.bar(self.data, self.counter, color='skyblue')
        plt.xlabel(self.key)
        plt.ylabel('Count')
        plt.title(f'Distribution of Sentences by {self.key} Level')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
    
        # Calculate the tick interval for approximately 20 ticks
        data_range = max(self.data) - min(self.data)
        tick_interval = max(1, int(data_range / 20))
        plt.xticks(np.arange(min(self.data), max(self.data) + 1, tick_interval))
    
        plt.show()

def best_sentences(search_str="", minimum=0.5, limit=10, highest=True) -> list:
    search_terms = search_str.split(" ")
    with open("data/sentences.tsv", "r", encoding="utf-8") as file:
        # Skip the first line and process the rest
        lines = [line.split("\t") for line in file.read().splitlines()[1:]]

    filtered_sentences = [
        (line[0], line[1], line[2], line[4]) for line in lines
        if all(term in line[0] for term in search_terms) and float(line[4]) >= minimum
    ]

    if highest:
        filtered_sentences.sort(key=lambda x: x[3], reverse=True)
    else:
        random.shuffle(filtered_sentences)

    return filtered_sentences[:limit]


def hsk_grabber(target_hsk, search_str="", deviation=0.2, limit=10):
    search_terms = search_str.split(" ")
    with open("data/sentences.tsv", "r", encoding="utf-8") as file:
        lines = [line.split("\t") for line in file.read().splitlines()[1:]]

    filtered_sentences = [
        (line[0], line[1], line[2], line[3]) for line in lines
        if all(term in line[0] for term in search_terms) and
           (target_hsk - deviation) < float(line[3]) < (target_hsk + deviation)
    ]

    random.shuffle(filtered_sentences)

    return filtered_sentences[:limit]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--visualize", action='store_true', help="whether to visualize results")
    parser.add_argument("-l", "--location", default="data/known.txt", help="location for known user vocabulary")
    parser.add_argument("-t", "--typesplit", choices=['ch', 'wo'], default="wo", help="split sentences character by character (ch) or word by word (wo)")
    parser.add_argument("-s", "--sort", choices=['HSK', 'custom'], default="HSK", help="sort sentences by 'HSK' or 'custom' (user ratio)")
    parser.add_argument("--string", default="", help="string used when searching sentences, split words by space")
    parser.add_argument("--smallest", type=float, default=0.6, help="smallest ratio of sentences known when searching (default is 0.6)")
    parser.add_argument("-e", "--easy", action='store_true', help="output 'custom' sentences the user is most likely to understand (default True)")
    parser.add_argument("-i", "--include", action='store_true', help="add custom sentence ratio to `data/sentences.tsv`")
    parser.add_argument("--limit", type=int, default=10, help="number of sentences outputted")
    parser.add_argument("-m", "--mine", action='store_true', help="whether or not to mine sentences")
    parser.add_argument("-d", "--deviation", type=float, default=0.2, help="HSK/user ratio deviation when searching for sentences")
    parser.add_argument("--target", type=float, help="target HSK level when searching for sentences")
    parser.add_argument("-o", "--output", choices=['HSK', 'custom'], default="HSK", help="output type & visualization type")
    return parser.parse_args()

def create_manager(args):
    try:
        with open(args.location, "r", encoding="utf-8"):
            return SentenceAssigner(args.location, args.typesplit == "ch")
    except IOError:
        print("Please provide a valid known words file!")
        sys.exit()

def main():
    args = parse_args()

    manager = create_manager(args)

    if args.include:
        manager.parse_document(custom=True)
    else:
        manager.parse_document()

    if args.sort == "custom":
        manager.custom = True
        manager.parse_document(custom=True)
    else:
        manager.parse_document()

    if args.sort == "custom":
        manager.sort_file(key="custom")
    else:
        manager.sort_file()

    if args.visualize:
        visualizer = DataVisualizer(key=args.output)
        visualizer.visualize()

    if args.mine:
        sentences = mine_sentences(args)
        for sentence in sentences:
            print(sentence, "\n")

def mine_sentences(args):
    if args.output == "custom":
        return best_sentences(args.string, minimum=args.smallest, limit=args.limit, highest=args.easy)
    else:
        target = args.target if args.target is not None else 3.5
        deviation = args.deviation if args.target is not None else 3.5
        return hsk_grabber(target, search_str=args.string, deviation=deviation, limit=args.limit)

if __name__ == "__main__":
    main()
