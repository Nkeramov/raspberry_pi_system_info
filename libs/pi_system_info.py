import time
import logging
import subprocess
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class PiSystemInfo(object):

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(PiSystemInfo, cls).__new__(cls)
        return cls.__instance

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    @staticmethod
    def __get_shell_cmd_output(command: str) -> Optional[str]:
        """Executes a shell command and returns its output. Handles errors."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Shell command '{command}' failed: {e}")
        except FileNotFoundError:
            logger.error(f"Command not found: {command}")

    def get_hostname(self) -> Optional[str]:
        """Retrieves the hostname using the 'hostname' command.

        Returns:
            The hostname, or None if the command fails.
        """
        command = "hostname"
        return self.__get_shell_cmd_output(command)

    def get_model(self) -> Optional[str]:
        """Retrieves the system model from /sys/firmware/devicetree/base/model.

        Returns:
            The system model, or None if the command fails or the file is not found.
        """
        command = "cat /sys/firmware/devicetree/base/model"
        return self.__get_shell_cmd_output(command)

    def get_os_name(self) -> Optional[str]:
        """Retrieves the pretty OS name from /etc/*-release.

        Returns:
            The pretty OS name, or None if the command fails.  Removes surrounding quotes.
        """
        command = "cat /etc/*-release | grep PRETTY_NAME | cut -d= -f2"
        return self.__get_shell_cmd_output(command).strip('"')

    def get_uptime_since(self) -> Optional[datetime]:
        """Retrieves the system uptime since boot, in YYYY-MM-DD HH:MM:SS format using 'uptime -s'.

        Returns:
            The uptime since boot, or None if the command fails.
        """
        command = "uptime -s"
        uptime_str = self.__get_shell_cmd_output(command)
        return datetime.strptime(uptime_str, "%Y-%m-%d %H:%M:%S")

    def get_uptime_pretty(self) -> Optional[str]:
        """Retrieves the system uptime in a human-readable format using 'uptime -p'.

        Returns:
            The pretty uptime, or None if the command fails.
        """
        command = "uptime -p"
        return self.__get_shell_cmd_output(command)

    def get_mac_address(self, interface='eth0') -> Optional[str]:
        """Retrieves the MAC address for a specified network interface.

        Args:
            interface: The network interface name (default: 'eth0').

        Returns:
            The MAC address, or None if the command fails or the interface is not found.
        """
        command = f"cat /sys/class/net/{interface}/address"
        return self.__get_shell_cmd_output(command)

    def get_ip_address(self, interface: str = 'eth0') -> Optional[str]:
        """Retrieves the IP address for a specified network interface.

        Args:
            interface: The network interface name (default: 'eth0').

        Returns:
            The IP address, or None if the command fails or the interface is not found.
        """
        command = f"ifconfig {interface} | grep 'inet ' | awk '{{print $2}}'"
        return self.__get_shell_cmd_output(command)

    def get_cpu_model_name(self) -> Optional[str]:
        """Retrieves the CPU model name from /proc/cpuinfo.

        Returns:
            The CPU model name, or None if the command fails.
        """
        command = "cat /proc/cpuinfo | grep 'model name' | cut -d: -f2"
        return self.__get_shell_cmd_output(command)

    def get_cpu_hardware_type(self) -> Optional[str]:
        """Retrieves the CPU hardware type from /proc/cpuinfo.

        Returns:
            The CPU hardware type, or None if the command fails.
        """
        command = "cat /proc/cpuinfo | grep 'Hardware' | cut -d: -f2"
        return self.__get_shell_cmd_output(command)

    def get_cpu_revision(self) -> Optional[str]:
        """Retrieves the CPU revision from /proc/cpuinfo.

        Returns:
            The CPU revision, or None if the command fails.
        """
        command = "cat /proc/cpuinfo | grep 'Revision' | cut -d: -f2"
        return self.__get_shell_cmd_output(command)

    def get_cpu_serial_number(self) -> Optional[str]:
        """Retrieves the CPU serial number from /proc/cpuinfo.

        Returns:
            The CPU serial number, or None if the command fails.
        """
        command = "cat /proc/cpuinfo | grep 'Serial' | cut -d: -f2"
        return self.__get_shell_cmd_output(command)

    def get_cpu_core_count(self) -> Optional[int]:
        """Retrieves the number of CPU cores using 'nproc'.

        Returns:
            The number of CPU cores, or None if the command fails.
        """
        command = "nproc"
        result = self.__get_shell_cmd_output(command)
        return int(result) if result is not None else result

    def get_cpu_core_voltage(self) -> Optional[float]:
        """Retrieves the CPU core voltage using 'vcgencmd'.

        Returns:
            The CPU core voltage, or None if the command fails.
        """
        command = "vcgencmd measure_volts| cut -d= -f2"
        result = self.__get_shell_cmd_output(command)
        return float(result[:-1]) if result is not None else result

    def get_cpu_temperature(self) -> Optional[float]:
        """Retrieves the CPU temperature using 'vcgencmd'.

        Returns:
            The CPU temperature, or None if the command fails.
        """
        command = "vcgencmd measure_temp | cut -d= -f2 | cut -d\\' -f1"
        result = self.__get_shell_cmd_output(command)
        return float(result) if result is not None else result

    def get_cpu_core_frequency(self, unit: str = 'MHz') -> Optional[int]:
        """Returns CPU frequency info in specified units (Hz, KHz, MHz or GHz).

        Args:
            unit: The desired unit for the frequency (Hz, KHz, MHz, GHz). Defaults to 'MHz'.

        Returns:
            The CPU core frequency in the specified unit, or None if the command fails or the unit is invalid.
        """
        command = "vcgencmd measure_clock arm | cut -d= -f2"
        result = self.__get_shell_cmd_output(command)
        if result is not None:
            frequency = int(result)
            match unit:
                case 'Hz':
                    return frequency
                case 'KHz':
                    return frequency // 10**3
                case 'MHz':
                    return frequency // 10**6
                case 'GHz':
                    return frequency // 10**9
                case _:
                    logger.error(f"Requested unknown cpu frequency unit: {unit}")

    def get_cpu_usage(self) -> Optional[str]:
        """Retrieves the CPU usage using 'top'.

        Returns:
            The CPU usage, or None if the command fails.  Note that the output format is dependent on 'top'.
        """
        command = "top -b -n2 | grep 'Cpu(s)'| tail -n 1 | awk '{print $2 + $4 }'"
        return self.__get_shell_cmd_output(command)

    def get_ram_info(self, unit: str = 'm') -> Optional[Dict[str, Optional[str]]]:
        """Returns RAM info in specified units (b, k, m, g). Uses a safer approach."""
        if unit not in ['b', 'k', 'm', 'g']:
            logger.error(f"Requested unknown ram volume unit: {unit}")
            return None

        command = f"free -{unit}"
        output = self.__get_shell_cmd_output(command)
        if output is None:
            return None

        try:
            lines = output.splitlines()
            fields = lines[1].split()
            return {
                'total': fields[1],
                'used': fields[2],
                'free': fields[3],
                'cache': fields[5],
                'available': fields[6],
            }
        except (IndexError, ValueError):
            logger.error(f"Failed to parse 'free' command output: {output}")
            return None

    def get_disk_usage_info(self) -> Optional[List[List[str]]]:
        """Return disk usage info in human readable units."""
        command = "df -h"
        output = self.__get_shell_cmd_output(command)
        if output is None:
            return None
        try:
            return [line.split() for line in output.splitlines()[1:]]
        except IndexError:
            logger.error(f"Failed to parse 'df' command output: {output}")
            return None

    def get_running_process_info(self) -> Optional[List[List[str]]]:
        command = "ps -Ao user,pid,pcpu,pmem,comm,lstart --sort=-pcpu"
        output = self.__get_shell_cmd_output(command)
        if output is None:
            return None
        try:
            return [line.split() for line in output.splitlines()[1:]]
        except IndexError:
            logger.error(f"Failed to parse 'ps' command output: {output}")
            return None


def get_console_logger() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


if __name__ == "__main__":
    logger = get_console_logger()
    pi_sys_info = PiSystemInfo(logger)
    try:
        logger.info(f"Model: {pi_sys_info.get_model()}")
        logger.info(f"IP address: {pi_sys_info.get_ip_address('eth0')}")
        logger.info(f"MAC address: {pi_sys_info.get_mac_address('eth0')}")
        while True:
            logger.info(f"CPU: temperature {pi_sys_info.get_cpu_temperature()} \xb0C, "
                        f"frequency {pi_sys_info.get_cpu_core_frequency()} MHz, usage {pi_sys_info.get_cpu_usage()}%")
            ram_info = pi_sys_info.get_ram_info()
            logger.info(f"RAM: total {ram_info['total']} Mb, used {ram_info['used']} Mb, free {ram_info['free']} Mb")
            time.sleep(2)
    except KeyboardInterrupt:
        logger.info("Stopped...")
