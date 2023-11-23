import argparse
import json
import curses
from functools import partial


def read_jsonl(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            yield json.loads(line)


def run_menu(stdscr, item):
    curses.curs_set(0)  # 커서 숨기기
    current_row = 0
    while True:
        try:
            stdscr.clear()
            stdscr.addstr("Output: " + item["output"] + "\n\n")
            stdscr.addstr("실제정답: " + str(item["answer"]) + "\n\n")
        except Exception as e:
            print(e)
        for idx, row in enumerate(["정답이 맞았어?", "정답이 틀렸어?"]):
            try:
                if idx == current_row:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(str(row) + "\n")
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(row + "\n")
            except Exception as e:
                print(e)
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return current_row == 0


def main(stdscr, args):
    # 색상 설정
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    total_score = 0

    corrects = []
    incorrects = []

    for item in read_jsonl(file_path=args.result_path):
        correct = run_menu(stdscr, item)
        if correct:
            total_score += item["score"]
            corrects.append(item)
        else:
            incorrects.append(item)

        try:
            stdscr.addstr("\nCurrent Score: " + str(total_score) + "\n\n")
        except Exception as e:
            print(e)

        stdscr.refresh()
        stdscr.getch()  # 사용자 입력 대기
    stdscr.addstr("Final Score: " + str(total_score) + "\n")
    stdscr.refresh()
    stdscr.getch()

    with open(args.result_path.replace(".jsonl", ".txt"), "w") as f:
        f.write("Final Score: " + str(total_score) + "\n\n")
        f.write("Total problem num: " + str(len(corrects) + len(incorrects)) + "\n")
        f.write("Correct problem num: " + str(len(corrects)) + "\n")
        f.write("Incorrect problem num: " + str(len(incorrects)) + "\n\n")
        f.write(
            "Accuracy: " + str(len(corrects) / (len(corrects) + len(incorrects))) + "\n"
        )

        f.write("Incorrects:\n")
        for item in incorrects:
            f.write(f"    - id: {item['id']}\n")

        # f.write("\nCorrects:\n")
        # for item in corrects:
        #     f.write(f"    - id: {item['id']}\n")
        #     f.write(f"        pred: {item['output']}\n")
        #     f.write(f"        answer: {item['answer']}\n")
        #     f.write(f"        score: {item['score']}\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--result_path", type=str, required=True)

    args = parser.parse_args()

    curses.wrapper(partial(main, args=args))
