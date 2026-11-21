
import time
import traceback

from services.rag import search_curriculum, list_lessons


def test_operation(name, function, *args):
    print(f"\nTesting {name}...", flush=True)
    start = time.perf_counter()

    try:
        result = function(*args)

        print(
            f"PASS: {name} in "
            f"{time.perf_counter() - start:.2f}s",
            flush=True,
        )
        print(str(result)[:2000], flush=True)

    except Exception:
        print(f"FAILED: {name}", flush=True)
        traceback.print_exc()


if __name__ == "__main__":
    test_operation(
        "list_lessons",
        list_lessons,
        "Mathematics",
    )

    test_operation(
        "search_curriculum",
        search_curriculum,
        "Mathematics",
        "place value tens hundreds",
        2,
    )
