
import random

TOTAL = 1000
AVAILABILITY = [0.90, 0.60, 0.30]

def simulate(p, seed):

    random.seed(seed)

    link = []

    for i in range(TOTAL):
        value = random.random()

        if value < p:
            link.append(1)
        else:
            link.append(0)

    # Immediate transmission

    immediate_delivered = 0
    immediate_lost = 0

    for i in range(TOTAL):
        if link[i] == 1:
            immediate_delivered += 1
        else:
            immediate_lost += 1

    # Store-and-forward transmission

    queue = []
    delays = []

    for i in range(TOTAL):
        queue.append(i)

        if link[i] == 1:
            while len(queue) > 0:
                generated_time = queue.pop(0)
                delay = i - generated_time
                delays.append(delay)

    # Flush remaining queued readings

    time = TOTAL

    while len(queue) > 0:

        if random.random() < p:

            while len(queue) > 0:
                generated_time = queue.pop(0)
                delay = time - generated_time
                delays.append(delay)

        time += 1

    delayed = 0
    total_delay = 0

    for i in range(len(delays)):
        total_delay += delays[i]

        if delays[i] > 0:
            delayed += 1

    mean_delay = total_delay / TOTAL

    print("\nLink Availability:", p * 100, "%")

    print("IMMEDIATE TRANSMISSION")
    print("Delivered:", immediate_delivered)
    print("Lost:", immediate_lost)
    print("Mean delay: 0 minutes")

    print("\nSTORE-AND-FORWARD")
    print("Delivered:", len(delays))
    print("Delayed:", delayed)
    print("Lost:", 0)
    print("Mean delay:", round(mean_delay, 3), "minutes")


for i in range(3):
    simulate(AVAILABILITY[i], 42)
