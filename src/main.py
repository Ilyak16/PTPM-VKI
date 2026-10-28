from converter import Converter


def main():
    test_values = [
        150.0,
        100.7,
        100.6,
        65.7,
        1.5,
        0.1,
        -0.1,
        -15.5,
        -30.4,
        -30.5,
        -94.5,
    ]

    for val in test_values:
        result = Converter.do(val)
        print(f"Converter.do({val:6.1f}) -> {result:6d}")
    print("\nПроверка исключения при x = 0.0:")
    try:
        Converter.do(0.0)
    except ValueError as e:
        print(f"Converter.do(0.0) -> Успешно перехвачено исключение: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
