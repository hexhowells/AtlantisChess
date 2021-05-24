import json
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", type=str, help="search book for move, ex \"e4 c5\"")
    parser.add_argument("-book", action='store_true', help="show opening book")
    parser.add_argument("-create", action='store_true', help="create opening book")
    parser.add_argument("-lim", type=int, help="entry limit")

    return parser.parse_args()


def games():
	with open("../Data/lichess.csv", "r") as fp:
		for line in fp:
			yield line[:-1]


def generate_book(move_len):
	print("Generating book with depth limit {}...".format(move_len))
	book = {}
	win2idx = {'white': 0, 'draw': 1, 'black': 2}

	cc = 0
	for i, game in enumerate(games(), 1):
		cc = i
		winner, moves_ = game.split(',')
		#if (i % 10_000) == 0: break

		moves = moves_.split(' ')

		for i in range(1, move_len+1):
			move = ' '.join(moves[:i])

			if move in book:
				book[move][3] += 1
				book[move][win2idx[winner]] += 1
			else:
				book[move] = [0, 0, 0, 1]
				book[move][win2idx[winner]] += 1

	print("\nTotal number of games in database: {:,}\n".format(cc))
	print("Number of entries in opening book: {:,}".format(len(book)))

	return book


def show_opening_book(book, entries):
	print("\n{}white{}draw{}black{}total\n".format(" "*31, " "*10, " "*9, " "*6))

	book = sort_popularity(book)

	for i, (move, stats) in enumerate(book.items(), 1):
		if (i % entries) == 0: break
		total = stats[3]

		#if total < 10_000: break

		w = round((stats[0] / total) * 100, 2)
		d = round((stats[1] / total) * 100, 2)
		b = round((stats[2] / total) * 100, 2)
		print("{: 4}. {: <20} = {: 8}%  |  {: 8}%  |  {: 8}%  |  {:,}".format(i, move, w, d, b, total))


def sort_popularity(book):
	return dict(sorted(book.items(), key=lambda item: item[1][3], reverse=True))


def search_book(book, player_move, entry_requirement):
	for moves, stats in sort_popularity(book).items():
		p_len = len(player_move)# + 1
		move_list = moves.split(' ')
		p_move_list = player_move.split(' ')

		if player_move in moves[:p_len] and len(move_list) == len(p_move_list)+1:
			if stats[3] < entry_requirement: break

			w = round((stats[0] / stats[3]) * 100, 2)
			b = round((stats[2] / stats[3]) * 100, 2)
			per_win = round(w - b, 2)
			if per_win >= 0:
				print("{: <30} | white wins {}% more\t| {:,} entries".format(moves, per_win, stats[3]))
			else:
				print("{: <30} # black wins {}% more\t| {:,} entries".format(moves, abs(per_win), stats[3]))



def load_book():
	with open("../Data/OpeningBook.json", 'r') as bookfile:
			book = json.load(bookfile)

	return book


def save_book(book):
	with open("../Data/OpeningBook.json", 'w') as bookfile:
		json.dump(book, bookfile)



if __name__ == "__main__":
	args = parse_args()

	if args.create and args.lim:
		book = generate_book(args.lim)
		save_book(book)
	elif args.create:
		print("argument -lim required!")

	book = load_book()

	
	if args.m and args.lim:
		search_book(book, args.m, args.lim)
	elif args.m:
		search_book(book, args.m, 100)
	elif args.book and args.lim:
		show_opening_book(book, args.lim)
	elif args.book:
		show_opening_book(book, 100)
	
