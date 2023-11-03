from dotenv import load_dotenv
import os
load_dotenv()


ignore = os.getenv('IGNORE_NAMESPACES')
print (ignore)
# for item in ignore:
#     print(item)


FILES = ignore.split(",")
print(FILES)
print(type(FILES))
for item in FILES:
    print(item)