from trivago2 import search_trivago

def main():
    city = "Viña del Mar"
    checkin = "2020-08-10"
    checkout = "2020-08-22"
    rooms = 2
    adults = 2
    children = 2
    babies = 1

    search_trivago(city, checkin, checkout, adults, children, babies)

if __name__ == "__main__":
    main()