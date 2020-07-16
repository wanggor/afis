    # 1 : {
    #     "zero-tick" : 0.2,
    #     "one-tick" : 0.7,
    #     "space-tick" : 0.4,
    #     "split-tick" : 0.4,
    #     "tolerance" : 0.15
    # },

mode_detection = {
    1 : {
        "zero-tick" : 0.2,
        "one-tick" : 0.7,
        "space-tick" : 0.3,
        "split-tick" : 0.3,
        "tolerance" : 0.15
    },

    2 : {
       "zero-tick" : 0.1,
        "one-tick" : 0.3,
        "space-tick" : 0.15,
        "split-tick" : 0.15,
        "tolerance" : 0.08
    },
    3 : {
        "zero-tick" : 0.02,
        "one-tick" : 0.15,
        "space-tick" : 0.05,
        "split-tick" : 0.05,
        "tolerance" : 0.05
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