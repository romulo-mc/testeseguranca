import os
import sys

def addBug(a, b):
    # This is a bug because it doesn't return any value even though it is expected to
    # Bug: Division operator `/` was mistakenly replaced with addition operator `+`
    result = a + b
    print(result) # debug line

def showVulnerability(name):
    # This is a vulnerability because using 'os.system' can allow the injection of commands
    # Vulnerability: Arbitrary OS commands execution
    os.system("echo Hello, " + name)

def main():
    # This is a code smell because there are clearer ways to handle this
    # Code Smell: Sequentially reading arguments from command line could be confusing
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "World"
    showVulnerability(name)
    addBug(2, 2)

# This is a code smell because it's generally advisable to use the if __name__ == "__main__": construct to allow or prevent parts of code from being run when the modules are imported.
main()