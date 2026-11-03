/* Read-only, bounded classification of MHI2 navigation URLs for AX1800M diagnostics.
 * Does not collect or log raw URLs, phone identities, UUIDs or transport data. */
#ifndef AX_HU_PRESENTATION_DIAG_H
#define AX_HU_PRESENTATION_DIAG_H
#include <stddef.h>
#include <string.h>
enum ax_hu_surface { AX_HU_UNKNOWN, AX_HU_BASE, AX_HU_MAP, AX_HU_INSTRUCTIONCARD };
enum ax_hu_toggle { AX_HU_UNSET, AX_HU_YES, AX_HU_NO, AX_HU_USER };
enum ax_hu_maneuver { AX_HU_MANEUVER_UNSET, AX_HU_MANEUVER_NONE, AX_HU_LEFT, AX_HU_RIGHT, AX_HU_TOP };
struct ax_hu_presentation {
    enum ax_hu_surface surface;
    enum ax_hu_toggle eta, speed_limit, compass;
    enum ax_hu_maneuver maneuver;
    unsigned query_present;
};
static int ax_hu_presentation_parse(const char *url,struct ax_hu_presentation *out) {
    static const char prefix[]="maps:/car/instrumentcluster";
    struct ax_hu_presentation a={0};
    const char *p;size_t n;unsigned seen=0;
    if(!out)return 0;
    memset(out,0,sizeof *out);
    if(!url)return 0;
    for(n=0;n<384 && url[n];++n){}
    if(n==384||n<sizeof(prefix)-1||memcmp(url,prefix,sizeof(prefix)-1))return 0;
    p=url+sizeof(prefix)-1;
    if(!strncmp(p,"/instructioncard",16)){p+=16;a.surface=AX_HU_INSTRUCTIONCARD;}
    else if(!strncmp(p,"/map",4)){p+=4;a.surface=AX_HU_MAP;}
    else a.surface=AX_HU_BASE;
    if(!*p){*out=a;return 1;}
    if(*p!='?'||a.surface==AX_HU_INSTRUCTIONCARD)return 0;
    a.query_present=1;++p;if(!*p)return 0;
    while(*p){
        const char *end=strchr(p,'&'),*eq;size_t k,v,len;unsigned bit;enum ax_hu_toggle toggle=AX_HU_UNSET;
        if(!end)end=p+strlen(p);
        len=(size_t)(end-p);eq=memchr(p,'=',len);
        if(!eq||eq==p)return 0;
        k=(size_t)(eq-p);v=(size_t)(end-eq-1);
        if(k==7&&!memcmp(p,"showETA",7))bit=1;
        else if(k==14&&!memcmp(p,"showSpeedLimit",14))bit=2;
        else if(k==11&&!memcmp(p,"showCompass",11))bit=4;
        else if(k==14&&!memcmp(p,"maneuverLayout",14))bit=8;
        else return 0;
        if(seen&bit)return 0;
        seen|=bit;
        if(bit==8){
            if(!v)a.maneuver=AX_HU_MANEUVER_NONE;
            else if(v==11&&!memcmp(eq+1,"leftAligned",11))a.maneuver=AX_HU_LEFT;
            else if(v==12&&!memcmp(eq+1,"rightAligned",12))a.maneuver=AX_HU_RIGHT;
            else if(v==10&&!memcmp(eq+1,"topAligned",10))a.maneuver=AX_HU_TOP;
            else return 0;
        }else {
            if(v==3&&!memcmp(eq+1,"yes",3))toggle=AX_HU_YES;
            else if(v==2&&!memcmp(eq+1,"no",2))toggle=AX_HU_NO;
            else if(v==4&&!memcmp(eq+1,"user",4))toggle=AX_HU_USER;
            else return 0;
            if(bit==1)a.eta=toggle;else if(bit==2)a.speed_limit=toggle;else a.compass=toggle;
        }
        if(!*end)break;
        p=end+1;
        if(!*p)return 0;
    }
    *out=a;return 1;
}
static const char *ax_hu_surface_name(enum ax_hu_surface v) {
    switch(v){case AX_HU_BASE:return "base";case AX_HU_MAP:return "map";case AX_HU_INSTRUCTIONCARD:return "instructioncard";default:return "unknown";}
}
static const char *ax_hu_toggle_name(enum ax_hu_toggle v) {
    switch(v){case AX_HU_YES:return "yes";case AX_HU_NO:return "no";case AX_HU_USER:return "user";default:return "unset";}
}
static const char *ax_hu_maneuver_name(enum ax_hu_maneuver v) {
    switch(v){case AX_HU_MANEUVER_NONE:return "none";case AX_HU_LEFT:return "left";case AX_HU_RIGHT:return "right";case AX_HU_TOP:return "top";default:return "unset";}
}
#endif
