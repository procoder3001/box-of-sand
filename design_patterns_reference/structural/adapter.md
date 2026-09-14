# Adapter

## Plain-English idea

An adapter is a small translator. It lets your code use an object whose method
names or data format do not match what your code expects.

## Everyday worked example: show a legacy thermometer on a new display

```python
class LegacyThermometer:
    def read_celsius(self) -> float:
        return 21.5


class WeatherScreen:
    def show_temperature_fahrenheit(self, temperature: float) -> None:
        print(f"Outside temperature: {temperature:.1f}°F")


class FahrenheitThermometer:
    def __init__(self, old_thermometer: LegacyThermometer) -> None:
        self.old_thermometer = old_thermometer

    def read_fahrenheit(self) -> float:
        celsius = self.old_thermometer.read_celsius()
        return celsius * 9 / 5 + 32


old_sensor = LegacyThermometer()
adapted_sensor = FahrenheitThermometer(old_sensor)
screen = WeatherScreen()
screen.show_temperature_fahrenheit(adapted_sensor.read_fahrenheit())
```

The new screen never learns that the old sensor uses Celsius or calls its
unfriendly method name. The adapter contains both translations.

## MLOps / SDK worked example: present an SDK response as package data

```python
class StorageSdk:
    def download_as_bytes(self, remote_path: str) -> bytes:
        print(f"SDK downloads {remote_path}")
        return b"accuracy=0.91\nloss=0.12"


class MetricsFile:
    def __init__(self, sdk: StorageSdk) -> None:
        self.sdk = sdk

    def read_metrics(self, name: str) -> dict[str, float]:
        raw_text = self.sdk.download_as_bytes(name).decode("utf-8")
        pairs = (line.split("=") for line in raw_text.splitlines())
        return {key: float(value) for key, value in pairs}


metrics = MetricsFile(StorageSdk()).read_metrics("runs/17/metrics.txt")
print(metrics["accuracy"])
```

## What problem does it solve?

An adapter prevents a third-party SDK’s response objects and vocabulary from
spreading through the rest of your package. It is also the natural place to
translate its exceptions into your package’s exceptions.

## When to use / not use it

Use one when an external dependency is substantial or you need a stable,
package-owned interface. Do not create an adapter for one simple call used in
one leaf function. Keep adapters deliberately narrow.

## Test it

Test the adapter with representative SDK data and errors. Then test your
service with a small fake that has the adapter’s interface; it should not need
to know about the real SDK at all.
