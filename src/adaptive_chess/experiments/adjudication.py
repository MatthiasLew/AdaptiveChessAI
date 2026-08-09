VALID_RESULTS = {"1-0", "0-1", "1/2-1/2"}


def adjudicate_result_by_material(
    final_material_balance: int,
    material_threshold: int = 3,
) -> str:
    """
    Wyznacza techniczny wynik partii na podstawie końcowej przewagi materialnej.

    Funkcja jest używana dla partii przerwanych limitem półruchów.
    Dodatnia przewaga oznacza przewagę białych.
    Ujemna przewaga oznacza przewagę czarnych.

    Args:
        final_material_balance: Końcowa przewaga materialna z perspektywy białych.
        material_threshold: Minimalna przewaga materiałowa wymagana do przyznania wygranej.

    Returns:
        "1-0", jeśli białe mają wystarczającą przewagę.
        "0-1", jeśli czarne mają wystarczającą przewagę.
        "1/2-1/2", jeśli przewaga jest zbyt mała.

    Raises:
        ValueError: Jeśli próg materiałowy jest mniejszy niż 1.
    """
    if material_threshold < 1:
        raise ValueError("material_threshold must be at least 1.")

    if final_material_balance >= material_threshold:
        return "1-0"

    if final_material_balance <= -material_threshold:
        return "0-1"

    return "1/2-1/2"