import PullingData

def main():
    losses = PullingData.pullLosses()
    gains = PullingData.pullGains()

    print(losses)
    print(gains)


if __name__ == "__main__": main() 