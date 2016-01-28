

def get_filename(speaker, smd, repetition):
    """
    available speakers: "Visaton BF45", "70s"
    """
    path = "O:/Diplomanden/Logeshwaran.Thamilselvan/Loudspeaker nonlinearity/Measurements/%s/output/%s_SMD%i_Index%i_TimeSignal"
    smds = {"Noise120s": 4,
            "Sweep16": 5,
            "Sweep18": 6,
            "Sweep20": 7,
            "Noise18": 8,
            "Noise20": 9,
            "Music1": 10,
            "Speech1": 11,
            "Speech2": 12,
            "Speech3": 13}
    return path % (speaker, speaker, smds[smd], repetition)