#include "../src/hu_presentation_diag.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void valid(const char *url,enum ax_hu_surface s,enum ax_hu_toggle eta,enum ax_hu_maneuver m) {
    struct ax_hu_presentation a;assert(ax_hu_presentation_parse(url,&a));assert(a.surface==s&&a.eta==eta&&a.maneuver==m);
}
static void invalid(const char *url) {
    struct ax_hu_presentation a;assert(!ax_hu_presentation_parse(url,&a));assert(a.surface==AX_HU_UNKNOWN&&a.eta==AX_HU_UNSET);
}
int main(void) {
    char too_long[390];struct ax_hu_presentation a;
    valid("maps:/car/instrumentcluster",AX_HU_BASE,AX_HU_UNSET,AX_HU_MANEUVER_UNSET);
    valid("maps:/car/instrumentcluster/map",AX_HU_MAP,AX_HU_UNSET,AX_HU_MANEUVER_UNSET);
    valid("maps:/car/instrumentcluster/instructioncard",AX_HU_INSTRUCTIONCARD,AX_HU_UNSET,AX_HU_MANEUVER_UNSET);
    valid("maps:/car/instrumentcluster?showSpeedLimit=yes&showCompass=yes&showETA=yes&maneuverLayout=rightAligned",AX_HU_BASE,AX_HU_YES,AX_HU_RIGHT);
    valid("maps:/car/instrumentcluster?showSpeedLimit=yes&showCompass=yes&showETA=no&maneuverLayout=topAligned",AX_HU_BASE,AX_HU_NO,AX_HU_TOP);
    valid("maps:/car/instrumentcluster/map?showETA=user&maneuverLayout=",AX_HU_MAP,AX_HU_USER,AX_HU_MANEUVER_NONE);
    assert(ax_hu_presentation_parse("maps:/car/instrumentcluster?showETA=yes&showCompass=no&showSpeedLimit=user&maneuverLayout=leftAligned",&a));
    assert(a.speed_limit==AX_HU_USER&&a.compass==AX_HU_NO&&a.maneuver==AX_HU_LEFT);
    assert(!strcmp(ax_hu_surface_name(a.surface),"base")&&!strcmp(ax_hu_toggle_name(a.eta),"yes")&&!strcmp(ax_hu_maneuver_name(a.maneuver),"left"));
    invalid("maps:/car/instrumentcluster/other");invalid("maps:/car/instrumentcluster/map?showETA=yes&unknown=city");
    invalid("maps:/car/instrumentcluster?showETA=yes&showETA=no");invalid("maps:/car/instrumentcluster?showETA=YES");
    invalid("maps:/car/instrumentcluster?showETA=yes&");invalid("maps:/car/instrumentcluster/instructioncard?showETA=yes");
    invalid("maps:/car/instrumentcluster?showETA=yes%26private");invalid("maps:/car/instrumentcluster?maneuverLayout=left");
    invalid("maps:/car/instrumentcluster?showETA=");invalid("maps:/car/instrumentcluster?");invalid("https://example.org/mylocation");invalid(NULL);
    memset(too_long,'x',sizeof too_long-1);too_long[sizeof too_long-1]='\0';invalid(too_long);
    assert(!ax_hu_presentation_parse("maps:/car/instrumentcluster",NULL));
    puts("HU_PRESENTATION_DIAG_TEST_PASS");return 0;
}
