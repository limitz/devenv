#include "atmega_timer.h"

void lmtz_timer0_init(timer0_clock_t clk, uint8_t interval) {
	TCNT0 = 0;
	TCCR0A = 0;
	TCCR0B = (1 << WGM02) | (uint8_t)clk;
	OCR0A = interval;
	TIMSK0 = 1<<OCIE0A;
}

void lmtz_timer1_init(timer1_clock_t clk, uint16_t interval) {
	TCNT1 = 0;
	TCCR1A = 0;
	TCCR1B = (1 << WGM12) | (uint8_t)clk;
	OCR1A = interval;
	TIMSK1 = 1<<OCIE1A;
}

void lmtz_timer2_init(timer2_clock_t clk, uint8_t interval) {
	TCNT2 = 0;
	TCCR2A = 0;
	TCCR2B = (1 << WGM22) | (uint8_t)clk;
	OCR2A = interval;
	TIMSK2 = 1<<OCIE2A;
}

void lmtz_timer0_set_interval(uint8_t interval) {
	TCNT0 = 0;
	OCR0A = interval;
}

void lmtz_timer1_set_interval(uint16_t interval) {
	TCNT1 = 0;
	OCR1A = interval;
}

void lmtz_timer2_set_interval(uint8_t interval) {
	TCNT2 = 0;
	OCR2A = interval;
}

