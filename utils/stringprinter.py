import sys

def print_usage():
  print("Usage: stringprinter j (maxchar)")
  print(" - stringprinter j")
  print("   Join splitted lines to one liner.")
  print(" - stringprinter s (maxchar)")
  print("   Split lines with at most (maxchar) per line.")
  print("All inputs are from stdin, outputs to stdout.")


def do_split(maxchar):
  outputlines = []
  currentline = []
  currentlinelen = 0
  
  for line in sys.stdin:
    for token in line.split(' '):
      # + 1 to account for space (except last char)
      additional_len = len(token) + (1 if len(currentline) > 0 else 0)
      if (currentlinelen + additional_len) > maxchar:
        # join and reset current line!
        if len(currentline) > 0:
          outputlines.append(' '.join(currentline))
          additional_len -= 1
        currentline.clear()
        currentlinelen = 0
      currentline.append(token)
      currentlinelen += additional_len

    if len(currentline) > 0:
      outputlines.append(' '.join(currentline))
    currentline.clear()
    currentlinelen = 0

  for line in outputlines:
    print(line)


def do_join():
  newline = True
  for line in sys.stdin:
    line = line[:-1]
    if len(line) == 0:
      print()
      newline = True
    else:
      if newline == True:
        newline = False
      else:
        print(" ", end="")
      print(line, end="")


def main():
  if len(sys.argv) < 2:
    print_usage()
    return

  args = list(sys.argv)
  args.pop(0)
  mode = args.pop(0)
  if mode == "s":
    try:
      maxchar = int(args.pop(0))
    except:
      print_usage()
      return
    do_split(maxchar)
  elif mode == "j":
    do_join()
  else:
    print_usage()
    return


if __name__ == "__main__":
  main()
