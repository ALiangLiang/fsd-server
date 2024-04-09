from aircrafts.aircraft import Aircraft
from utils.physics import Speed


class B738 (Aircraft):
    icao_name = 'B738'
    type = 'M'
    mtow = 70530
    to0 = 26000 * 2
    to1 = 24000 * 2
    to2 = 22000 * 2
    climb_roc = Speed(fpm=1096.976)
    descent_roc = Speed(fpm=-1716.989)
    drag_coefficient = 0.076
    vr = Speed(knots=145)
