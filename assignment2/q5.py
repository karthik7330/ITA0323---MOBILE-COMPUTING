
import math

ANTENNA_COUNTS = [2, 4, 8, 16]
SIR_THRESHOLD = 10

def array_factor(N, angle):

    x = math.pi * math.sin(math.radians(angle))

    real = 0
    imaginary = 0

    for n in range(N):
        real += math.cos(n * x)
        imaginary += math.sin(n * x)

    magnitude = math.sqrt(
        real * real + imaginary * imaginary
    )

    return magnitude / N


def calculate_beamwidth(N):

    threshold = 1 / math.sqrt(2)
    angle = 0.0

    while angle <= 90:

        response = array_factor(N, angle)

        if response <= threshold:
            return round(2 * angle, 2)

        angle += 0.01

    return 180


def calculate_sidelobe(N):

    if N == 2:
        return None

    first_null = math.degrees(
        math.asin(2 / N)
    )

    maximum = 0
    angle = first_null + 0.01

    while angle <= 90:

        response = array_factor(N, angle)

        if response > maximum:
            maximum = response

        angle += 0.01

    if maximum == 0:
        return None

    return round(20 * math.log10(maximum), 2)


def calculate_sir(N, separation):

    response = array_factor(N, separation)

    if response < 0.000000001:
        return 300

    sir = -20 * math.log10(response)

    return round(sir, 2)


def main():

    print("SDMA ARRAY ANALYSIS")
    print("SIR Threshold:", SIR_THRESHOLD, "dB")

    print("\nBEAMWIDTH AND SIDELOBE RESULTS")

    for N in ANTENNA_COUNTS:

        beamwidth = calculate_beamwidth(N)
        sidelobe = calculate_sidelobe(N)

        print("\nAntenna Elements:", N)
        print("Beamwidth:", beamwidth, "degrees")

        if sidelobe is None:
            print("Sidelobe: Not applicable")
        else:
            print("Maximum Sidelobe:", sidelobe, "dB")

    print("\nSIR FOR DIFFERENT ANGULAR SEPARATIONS")

    print("Elements | Angle | SIR | Decision")

    for N in ANTENNA_COUNTS:

        for angle in range(5, 65, 5):

            sir = calculate_sir(N, angle)

            if sir >= SIR_THRESHOLD:
                decision = "SHARE"
            else:
                decision = "DO NOT SHARE"

            print(
                N, "|",
                angle, "|",
                sir, "dB |",
                decision
            )

    print("\nMINIMUM ANGULAR SEPARATION")

    for N in ANTENNA_COUNTS:

        minimum = None

        for angle in range(5, 65, 5):

            sir = calculate_sir(N, angle)

            if sir >= SIR_THRESHOLD:
                minimum = angle
                break

        print(
            "Elements:", N,
            "Minimum Separation:", minimum, "degrees"
        )


main()
