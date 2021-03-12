    # 1 : {
    #     "zero-tick" : 0.2,
    #     "one-tick" : 0.7,
    #     "space-tick" : 0.4,
    #     "split-tick" : 0.4,
    #     "tolerance" : 0.15
    # },

mode_detection = {
    1 : {
        "zero-tick" : 0.4,
        "one-tick" : 1,
        "space-tick" : 1.3,
        "split-tick" : 1.3,
        "tolerance" : 0.3
    },
    2 : {
       "zero-tick" : 0.3,
        "one-tick" : 0.6,
        "space-tick" : 1,
        "split-tick" : 1,
        "tolerance" : 0.1
    },
    3 : {
        "zero-tick" : 0.2,
        "one-tick" : 0.4,
        "space-tick" : 0.9,
        "split-tick" : 0.9,
        "tolerance" : 0.1
    }
}

color_option = {
    1 : {
        "H" : 0,
        "S" : 0,
        "V" : 240,
        "Hmax" : 180,
        "Smax" : 20,
        "Vmax" : 255
    },
    2 : {
        "H" : 0,
        "S" : 0,
        "V" : 90,
        "Hmax" : 255,
        "Smax" : 255,
        "Vmax" : 44
    },
}

shape_config = {
    "minSize" : 0.15,
    "maxSize" : 0.95,
    "shapeTolarance" : 0.3,
    "kernelSize" : 18,
    "blurr_core" : 6,
    "min-circle-coorection" : 0, 
    "center-correction" : 0.1
}