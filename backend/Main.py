import PullingData

def main():
    losses = PullingData.pullLosses()
    gains = PullingData.pullGains()
    difference = PullingData.calcDiff(losses, gains)


    print(losses)
    print("\n")
    print(gains)
    print("\n")
    print(difference)


if __name__ == "__main__": main() 