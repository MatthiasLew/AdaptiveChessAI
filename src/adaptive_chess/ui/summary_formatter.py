import chess


def color_to_polish(color: chess.Color) -> str:
    """
    Zwraca polską nazwę koloru.
    """
    if color == chess.WHITE:
        return "białe"

    if color == chess.BLACK:
        return "czarne"

    raise ValueError(f"Unsupported color: {color}")


def describe_result(result: str) -> str:
    """
    Zwraca czytelny opis wyniku partii.
    """
    if result == "1-0":
        return "Wygrana białych"

    if result == "0-1":
        return "Wygrana czarnych"

    if result == "1/2-1/2":
        return "Remis"

    if result == "*":
        return "Partia bez rozstrzygnięcia"

    return f"Nieznany wynik: {result}"


def describe_material_balance(balance: int) -> str:
    """
    Opisuje końcową przewagę materialną z perspektywy białych.
    """
    if balance > 0:
        return f"Białe +{balance}"

    if balance < 0:
        return f"Czarne +{abs(balance)}"

    return "Równy materiał"
