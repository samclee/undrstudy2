import os
import json

def clean_str(str):
  if str[0] == "\"" and str[-1] == "\"":
    return str[1:-1]

  return str

def clean_args(args):
  return map(clean_str, args)


def to_line(func_name, args):
  return [{"func_name": func_name, "args": args}]

def to_narrator_text(text):
  return [
    {"func_name": "show_none", "args": []},
    {"func_name": "hide_nameplate", "args": []},
    {"func_name": "text", "args": [text]}
  ]

def to_character_text(name, side, text):
  args = [name, side]
  return [
    {"func_name": "nameplate", "args": args},
    {"func_name": "text", "args": [text]}
  ]

def fill_quoted_spaces(str):
  str_ary = list(str)
  should_fill = False
  for i in range(len(str_ary)):
    char = str_ary[i]
    if char == ' ' and should_fill:
      str_ary[i] = "@"
    elif char == '"':
      should_fill = not should_fill
  return ''.join(str_ary)

def unfill_quoted_spaces(str_ary):
  new_ary = []

  for str in str_ary:
    new_str = str.replace("@", " ")
    new_ary.append(new_str)
  return new_ary

def map_char_and_emotion_to_portrait(name, emotion):
  return name + "_" + emotion

def transform(fname):
  fname_no_ext = fname[:-4]
  char_map = {}
  to_json = []
  with open(fname) as file:
    for raw_line in file:
      raw_line = fill_quoted_spaces(raw_line)
      raw_line_ary = raw_line.split()
      raw_line_ary = unfill_quoted_spaces(raw_line_ary)
      if len(raw_line_ary) == 0:
        continue

      cmd_name = raw_line_ary[0]
      # raw dialog
      if cmd_name[0] == "\"":
        text = clean_str(cmd_name)
        narrator_lines = to_narrator_text(text)
        to_json += narrator_lines
      # meta func
      elif cmd_name == "define":
        symbol = raw_line_ary[1]
        name = clean_str(raw_line_ary[2])
        side = raw_line_ary[3]
        char_map[symbol] = {"name": name, "side": side}
      # character dialog
      elif char_map.has_key(cmd_name):
        char = char_map[cmd_name]
        text = clean_str(raw_line_ary[1])
        char_lines = to_character_text(char["name"], char["side"], text)
        to_json += char_lines
      # show
      elif cmd_name == "show":
        name = char_map[raw_line_ary[1]]["name"]
        side = char_map[raw_line_ary[1]]["side"]
        portrait_name = map_char_and_emotion_to_portrait(name, raw_line_ary[2])

        func_line = to_line("myshow", [portrait_name, side])
        to_json += func_line
        func_line = to_line("active", [side])
        to_json += func_line
      else:
        func_line = to_line(cmd_name, raw_line_ary[1:])
        to_json += func_line


  json_str = json.dumps(to_json, indent=4)
  new_json = fname_no_ext + ".json"
  with open(new_json, 'w') as json_file:
    json_file.write(json_str)

for filename in os.listdir("."):
    if filename.endswith(".txt"):
        transform(filename)