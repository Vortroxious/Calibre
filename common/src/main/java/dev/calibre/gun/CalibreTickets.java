package dev.calibre.gun;

import software.bernie.geckolib.constant.dataticket.DataTicket;

/** Extra GeckoLib render-state data used by the gun renderer and animation controller. */
public final class CalibreTickets {
    public static final DataTicket<Boolean> EMPTY = DataTicket.create("calibre_empty", Boolean.class);
    public static final DataTicket<Boolean> FIRST_PERSON = DataTicket.create("calibre_first_person", Boolean.class);
    public static final DataTicket<GunAttachments> ATTACHMENTS = DataTicket.create("calibre_attachments", GunAttachments.class);
    public static final DataTicket<Float> FLASH = DataTicket.create("calibre_flash", Float.class);
    /** rounds left for the belt display (Integer.MAX_VALUE while reloading: the new belt is shown in full) */
    public static final DataTicket<Integer> ROUNDS = DataTicket.create("calibre_rounds", Integer.class);
    public static final DataTicket<Boolean> HIDE_ARMS = DataTicket.create("calibre_hide_arms", Boolean.class);

    private CalibreTickets() {}
}
