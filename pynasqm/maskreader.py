class MaskReader:
    def __init__(self, mask):
        self._mask = mask

    def type(self):
        if self._mask[0] == '@':
            return "atom"
        if self._mask[0] == ':':
            return "residue"
        raise ValueError("Mask must defined to be either atoms or "\
                         "residues")

    def get_list(self):
        list_commands = self._mask[1:].split(',')
        list_indexes = self._convert_commands(list_commands)
        return list_indexes

    def _convert_commands(self, list_commands):
        answer = []
        for command in list_commands:
            answer.extend(self._convert_range(command))
        return answer

    @staticmethod
    def _convert_range(command):
        if '-' not in command:
            return [int(command)]
        ranges = [int(x) for x in command.split('-')]
        return [x for x in range(ranges[0], ranges[1]+1)]
