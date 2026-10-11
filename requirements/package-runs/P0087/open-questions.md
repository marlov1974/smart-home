# Open questions

1. Which outbound personality/profile is active for this Geodan, and what physical controller receives each representation? Source firmware for frequency/brine control is absent.
2. Which gates make fixed-flow thermostat-off/restart, and does the room thermo-diff setting apply? B2700/3A4A is not yet sufficient evidence.
3. What interrupt/scheduler increments each descriptor timer? Raw180/300 counts cannot yet be seconds.
4. Are same-target CN105 writes observed by any timer outside B9BFE? Selected/accepted equality alone is not proof.
5. What selects profile2's held3947 and when is it refreshed? What initializes/transfers room-adaptation state throughDHW?
6. What writes49C7 and how does it relate to Water flow control? Mode-dependent pump correction is proven, closed-loop flow regulation is not.
7. What are raw sensor filter delay, full pump overrun, valve lead time, auxiliary-heater delay and native minimum run/off?
8. Which20.01 contracts remain externally stable on21.00? Internal addresses and constants have no installed-image verification.

These do not block the delivered FTC-side partial model, but prevent a faithful whole-machine frequency or stop predictor. No physical test has been silently substituted for missing evidence.
