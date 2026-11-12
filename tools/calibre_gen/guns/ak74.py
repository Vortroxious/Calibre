"""More of the Kalashnikov family from the kit in aks.py: AK-74M, AKS-74U, AK-12 and the RPK light machine gun."""
from ..common import GunAsset
from .aks import _ak, _anims

FP = {"hip": {"pos": [0.118, -0.128, -0.17], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.24}}


def ak74m():
    """AK-74M: 943 mm long, 415 mm barrel, black polymer furniture, side-folding butt, the big two-chamber brake."""
    m = _ak("ak74m", wood="polymer", grip="polymer", muzzle="ak74", stock="poly", mag="ak74")
    return GunAsset(m, _anims(m, 6.0, (2.6, 0.5, 1.1), 11, rec=0.14, length=0.22), FP)


def aks74u():
    """AKS-74U: 730 mm with the stock open, 206 mm barrel, flared muzzle booster, sights on the gas block and the
    hinged cover, steel skeleton stock."""
    m = _ak("aks74u", barrel_out=176, guard_len=120, gas_block=-246, muzzle="booster", stock="skeleton", mag="ak74",
            rear="flip", gb_sight=True, cover_ribs=False, swells=False, sight_y=54)
    fp = {"hip": {"pos": [0.118, -0.128, -0.19], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.1}}
    return GunAsset(m, _anims(m, 6.0, (3.0, 0.6, 1.3), 12, rec=0.14, length=0.22, draw_len=0.62), fp)


def ak12():
    """AK-12: 945 mm with the stock out, 415 mm barrel, railed cover and hand guard, adjustable stock, sights on the
    gas block and the rear of the rail."""
    m = _ak("ak12", wood="polymer", grip="polymer", muzzle="ak74", stock="tele", mag="ak74", rear="flip",
            gb_sight=True, cover_ribs=False, swells=False, rail=True, vented=True, sight_y=58, st="steel_dark")
    fp = {"hip": {"pos": [0.118, -0.128, -0.19], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.1}}
    return GunAsset(m, _anims(m, 6.0, (2.4, 0.45, 1.0), 10, rec=0.13, length=0.21), fp)


def rpk():
    """RPK: 1040 mm long, 590 mm heavy barrel, folding bipod, club-foot butt, 40-round magazine."""
    m = _ak("rpk", barrel_out=545, barrel_d=17.5, front_at=-625, muzzle="nut", stock="club", mag="rpk40",
            bipod_at=-590)
    fp = {"hip": {"pos": [0.12, -0.132, -0.18], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.24}}
    return GunAsset(m, _anims(m, 8.0, (2.8, 0.5, 1.2), 11, rec=0.15, length=0.24, draw_len=0.85), fp)


GUNS = {"ak74m": ak74m, "aks74u": aks74u, "ak12": ak12, "rpk": rpk}
