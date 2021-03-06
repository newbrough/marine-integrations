#!/usr/bin/env python

"""
@package mi.instrument.nobska.mavs4.mavs4.test.test_driver
@file /Users/Bill/WorkSpace/marine-integrations/mi/instrument/nobska/mavs4/mavs4/driver.py
@author Bill Bollenbacher
@brief Test cases for mavs4 driver
 
USAGE:
 Make tests verbose and provide stdout
   * From the IDK
       $ bin/test_driver
       $ bin/test_driver -u
       $ bin/test_driver -i
       $ bin/test_driver -q

   * From pyon
       $ bin/nosetests -s -v /Users/Bill/WorkSpace/marine-integrations/mi/instrument/nobska/mavs4
       $ bin/nosetests -s -v /Users/Bill/WorkSpace/marine-integrations/mi/instrument/nobska/mavs4 -a UNIT
       $ bin/nosetests -s -v /Users/Bill/WorkSpace/marine-integrations/mi/instrument/nobska/mavs4 -a INT
       $ bin/nosetests -s -v /Users/Bill/WorkSpace/marine-integrations/mi/instrument/nobska/mavs4 -a QUAL
"""

__author__ = 'Bill Bollenbacher'
__license__ = 'Apache 2.0'

"""
#from mock import Mock, call, DEFAULT

#from nose.plugins.attrib import attr

from ion.idk.metadata import Metadata
from ion.idk.comm_config import CommConfig
from ion.idk.unit_test import InstrumentDriverTestCase
from ion.idk.test.driver_qualification import DriverQualificationTestCase

#from mi.instrument.nobska.mavs4.mavs4.driver import State
#from mi.instrument.nobska.mavs4.mavs4.driver import Event
#from mi.instrument.nobska.mavs4.mavs4.driver import Error
#from mi.instrument.nobska.mavs4.mavs4.driver import Status
#from mi.instrument.nobska.mavs4.mavs4.driver import Prompt
#from mi.instrument.nobska.mavs4.mavs4.driver import Channel
#from mi.instrument.nobska.mavs4.mavs4.driver import Command
#from mi.instrument.nobska.mavs4.mavs4.driver import Parameter
#from mi.instrument.nobska.mavs4.mavs4.driver import Capability
#from mi.instrument.nobska.mavs4.mavs4.driver import MetadataParameter
#from mi.instrument.nobska.mavs4.mavs4.driver import mavs4InstrumentProtocol
#from mi.instrument.nobska.mavs4.mavs4.driver import mavs4InstrumentDriver


# Standard imports.
#import os
#import signal
import time
import unittest
#from datetime import datetime

# 3rd party imports.
#from gevent import spawn
#from gevent.event import AsyncResult
import gevent
from nose.plugins.attrib import attr
#from mock import patch
#import uuid

# ION imports.
#from interface.objects import StreamQuery
#from interface.services.dm.itransform_management_service import TransformManagementServiceClient
#from interface.services.cei.iprocess_dispatcher_service import ProcessDispatcherServiceClient
#from interface.services.icontainer_agent import ContainerAgentClient
#from interface.services.dm.ipubsub_management_service import PubsubManagementServiceClient
#from pyon.public import StreamSubscriberRegistrar
from prototype.sci_data.stream_defs import ctd_stream_definition
#from pyon.agent.agent import ResourceAgentClient
#from interface.objects import AgentCommand
#from pyon.util.int_test import IonIntegrationTestCase
#from pyon.util.context import LocalContextMixin
#from pyon.public import CFG
#from pyon.event.event import EventSubscriber, EventPublisher

#from pyon.core.exception import InstParameterError


# MI imports.
#from ion.agents.port.logger_process import EthernetDeviceLogger
#from ion.agents.instrument.instrument_agent import InstrumentAgentState
from mi.instrument.nobska.mavs4.ooicore.driver import InstrumentParameters
from mi.idk.unit_test import InstrumentDriverTestCase
from mi.idk.unit_test import InstrumentDriverUnitTestCase
from mi.idk.unit_test import InstrumentDriverIntegrationTestCase
from mi.idk.unit_test import InstrumentDriverQualificationTestCase
from mi.core.log import log

from mi.instrument.nobska.mavs4.ooicore.driver import PACKET_CONFIG
"""

# Ensure the test class is monkey patched for gevent
from gevent import monkey; monkey.patch_all()
import gevent
import socket

# Standard lib imports
import time
import unittest

# 3rd party imports
from nose.plugins.attrib import attr

from prototype.sci_data.stream_defs import ctd_stream_definition

from mi.core.instrument.instrument_driver import DriverAsyncEvent
from mi.core.instrument.instrument_driver import DriverConnectionState

from mi.core.exceptions import InstrumentException
from mi.core.exceptions import InstrumentTimeoutException
from mi.core.exceptions import InstrumentParameterException
from mi.core.exceptions import InstrumentStateException
from mi.core.exceptions import InstrumentCommandException

from mi.instrument.seabird.sbe37smb.ooicore.driver import PACKET_CONFIG
from mi.instrument.seabird.sbe37smb.ooicore.driver import SBE37Driver
from mi.instrument.seabird.sbe37smb.ooicore.driver import SBE37ProtocolState
from mi.instrument.seabird.sbe37smb.ooicore.driver import SBE37Parameter

from mi.idk.unit_test import InstrumentDriverTestCase
from mi.idk.unit_test import InstrumentDriverUnitTestCase
from mi.idk.unit_test import InstrumentDriverIntegrationTestCase
from mi.idk.unit_test import InstrumentDriverQualificationTestCase

# MI logger
from mi.core.log import get_logger ; log = get_logger()
from interface.objects import AgentCommand

from ion.agents.instrument.instrument_agent import InstrumentAgentState

from ion.agents.instrument.direct_access.direct_access_server import DirectAccessTypes


## Initialize the test configuration
InstrumentDriverTestCase.initialize(
    driver_module='mi.instrument.nobska.mavs4.ooicore.driver',
    driver_class="mavs4InstrumentDriver",

    instrument_agent_resource_id = '123xyz',
    instrument_agent_name = 'Agent007',
    instrument_agent_packet_config = PACKET_CONFIG,
    instrument_agent_stream_definition = ctd_stream_definition(stream_id=None)
)


class TcpClient():
    # for direct access testing
    buf = ""

    def __init__(self, host, port):
        self.buf = ""
        self.host = host
        self.port = port
        # log.debug("OPEN SOCKET HOST = " + str(host) + " PORT = " + str(port))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        self.s.settimeout(0.0)

    def read_a_char(self):
        temp = self.s.recv(1024)
        if len(temp) > 0:
            log.debug("read_a_char got '" + str(repr(temp)) + "'")
            self.buf += temp
        if len(self.buf) > 0:
            c = self.buf[0:1]
            self.buf = self.buf[1:]
        else:
            c = None

        return c

    def peek_at_buffer(self):
        if len(self.buf) == 0:
            try:
                self.buf = self.s.recv(1024)
                log.debug("RAW READ GOT '" + str(repr(self.buf)) + "'")
            except:
                """
                Ignore this exception, its harmless
                """

        return self.buf

    def remove_from_buffer(self, remove):
        log.debug("BUF WAS " + str(repr(self.buf)))
        self.buf = self.buf.replace(remove, "")
        log.debug("BUF IS '" + str(repr(self.buf)) + "'")

    def get_data(self):
        data = ""
        try:
            ret = ""

            while True:
                c = self.read_a_char()
                if c == None:
                    break
                if c == '\n' or c == '':
                    ret += c
                    break
                else:
                    ret += c

            data = ret
        except AttributeError:
            log.debug("CLOSING - GOT AN ATTRIBUTE ERROR")
            self.s.close()
        except:
            data = ""

        if data:
            data = data.lower()
            log.debug("IN  [" + repr(data) + "]")
        return data

    def send_data(self, data, debug):
        try:
            log.debug("OUT [" + repr(data) + "]")
            self.s.sendall(data)
        except:
            log.debug("*** send_data FAILED [" + debug + "] had an exception sending [" + data + "]")



#################################### RULES ####################################
#                                                                             #
# Common capabilities in the base class                                       #
#                                                                             #
# Instrument specific stuff in the derived class                              #
#                                                                             #
# Generator spits out either stubs or comments describing test this here,     #
# test that there.                                                            #
#                                                                             #
# Qualification tests are driven through the instrument_agent                 #
#                                                                             #
###############################################################################

###############################################################################
#                                UNIT TESTS                                   #
#         Unit tests test the method calls and parameters using Mock.         #
###############################################################################

@attr('UNIT', group='mi')
class Testmavs4_UNIT(InstrumentDriverTestCase):
    """Unit Test Container"""
    
    def setUp(self):
        """
        @brief initialize mock objects for the protocol object.
        """
        #self.callback = Mock(name='callback')
        #self.logger = Mock(name='logger')
        #self.logger_client = Mock(name='logger_client')
        #self.protocol = mavs4InstrumentProtocol()
    
        #self.protocol.configure(self.comm_config)
        #self.protocol.initialize()
        #self.protocol._logger = self.logger 
        #self.protocol._logger_client = self.logger_client
        #self.protocol._get_response = Mock(return_value=('$', None))
        
        # Quick sanity check to make sure the logger got mocked properly
        #self.assertEquals(self.protocol._logger, self.logger)
        #self.assertEquals(self.protocol._logger_client, self.logger_client)
        
    ###
    #    Add driver specific unit tests
    ###
    
    
###############################################################################
#                            INTEGRATION TESTS                                #
#     Integration test test the direct driver / instrument interaction        #
#     but making direct calls via zeromq.                                     #
#     - Common Integration tests test the driver through the instrument agent #
#     and common for all drivers (minimum requirement for ION ingestion)       #
###############################################################################

@attr('INT', group='mi')
class Testmavs4_INT(InstrumentDriverIntegrationTestCase):
    """Integration Test Container"""
    
    @staticmethod
    def driver_module():
        return 'mi.instrument.nobska.mavs4.ooicore.driver'
        
    @staticmethod
    def driver_class():
        return 'mavs4InstrumentDriver'    
    
    @unittest.skip("override & skip while in development")
    def test_driver_process(self):
        pass 
    
    def Xtest_instrumment_wakeup(self):
        """
        @brief Test for instrument wakeup, expects instrument to be in 'command' state
        """
        state = self.driver_client.cmd_dvr('get_current_state')
        self.assertEqual(state, DriverConnectionState.UNCONFIGURED)

        # Configure driver for comms and transition to disconnected.
        reply = self.driver_client.cmd_dvr('configure', self.port_agent_comm_config())

        # Test the driver is configured for comms and in disconnected state.
        state = self.driver_client.cmd_dvr('get_current_state')
        self.assertEqual(state, DriverConnectionState.DISCONNECTED)

        # Connect to instrument and transition to unknown.
        reply = self.driver_client.cmd_dvr('connect')

        # Test the driver is in unknown state.
        state = self.driver_client.cmd_dvr('get_current_state')
        self.assertEqual(state, SBE37ProtocolState.UNKNOWN)

        # discover instrument state and transition to command.
        reply = self.driver_client.cmd_dvr('discover')

        # Test the driver is in command mode.
        state = self.driver_client.cmd_dvr('get_current_state')
        self.assertEqual(state, SBE37ProtocolState.COMMAND)
                

    ###
    #    Add driver specific integration tests
    ###

###############################################################################
#                            QUALIFICATION TESTS                              #
# Device specific qualification tests are for                                 #
# testing device specific capabilities                                        #
###############################################################################

@attr('QUAL', group='mi')
class Testmavs4_QUAL(InstrumentDriverQualificationTestCase):
    """Qualification Test Container"""
    
    # Qualification tests live in the base class.  This class is extended
    # here so that when running this test from 'nosetests' all tests
    # (UNIT, INT, and QUAL) are run.  
    pass


    def test_direct_access_telnet_mode_manually(self):
        """
        @brief This test manually tests that the Instrument Driver properly supports direct access to the physical instrument. (telnet mode)
        """
        cmd = AgentCommand(command='power_down')
        retval = self.instrument_agent_client.execute_agent(cmd)
        cmd = AgentCommand(command='get_current_state')
        retval = self.instrument_agent_client.execute_agent(cmd)
        state = retval.result
        print("sent power_down; IA state = %s" %str(retval.result))
        self.assertEqual(state, InstrumentAgentState.POWERED_DOWN)

        cmd = AgentCommand(command='power_up')
        retval = self.instrument_agent_client.execute_agent(cmd)
        cmd = AgentCommand(command='get_current_state')
        retval = self.instrument_agent_client.execute_agent(cmd)
        state = retval.result
        print("sent power_up; IA state = %s" %str(retval.result))
        self.assertEqual(state, InstrumentAgentState.UNINITIALIZED)

        cmd = AgentCommand(command='initialize')
        retval = self.instrument_agent_client.execute_agent(cmd)
        cmd = AgentCommand(command='get_current_state')
        retval = self.instrument_agent_client.execute_agent(cmd)
        state = retval.result
        print("sent initialize; IA state = %s" %str(retval.result))
        self.assertEqual(state, InstrumentAgentState.INACTIVE)

        cmd = AgentCommand(command='go_active')
        retval = self.instrument_agent_client.execute_agent(cmd)
        cmd = AgentCommand(command='get_current_state')
        retval = self.instrument_agent_client.execute_agent(cmd)
        state = retval.result
        print("sent go_active; IA state = %s" %str(retval.result))
        self.assertEqual(state, InstrumentAgentState.IDLE)

        cmd = AgentCommand(command='run')
        retval = self.instrument_agent_client.execute_agent(cmd)
        cmd = AgentCommand(command='get_current_state')
        retval = self.instrument_agent_client.execute_agent(cmd)
        state = retval.result
        print("sent run; IA state = %s" %str(retval.result))
        self.assertEqual(state, InstrumentAgentState.OBSERVATORY)

        gevent.sleep(5)  # wait for mavs4 to go back to sleep if it was sleeping
        
        # go direct access
        cmd = AgentCommand(command='go_direct_access',
                           kwargs={'session_type': DirectAccessTypes.telnet,
                                   #kwargs={'session_type':DirectAccessTypes.vsp,
                                   'session_timeout':600,
                                   'inactivity_timeout':600})
        retval = self.instrument_agent_client.execute_agent(cmd)
        log.warn("go_direct_access retval=" + str(retval.result))
        
        gevent.sleep(600)  # wait for manual telnet session to be run


    def Xtest_direct_access_telnet_mode(self):
        """
        @brief This test verifies that the Instrument Driver properly supports direct access to the physical instrument. (telnet mode)
        """
        cmd = AgentCommand(command='power_down')
        retval = self.instrument_agent_client.execute_agent(cmd)
        cmd = AgentCommand(command='get_current_state')
        retval = self.instrument_agent_client.execute_agent(cmd)
        state = retval.result
        self.assertEqual(state, InstrumentAgentState.POWERED_DOWN)

        cmd = AgentCommand(command='power_up')
        retval = self.instrument_agent_client.execute_agent(cmd)
        cmd = AgentCommand(command='get_current_state')
        retval = self.instrument_agent_client.execute_agent(cmd)
        state = retval.result
        self.assertEqual(state, InstrumentAgentState.UNINITIALIZED)

        cmd = AgentCommand(command='initialize')
        retval = self.instrument_agent_client.execute_agent(cmd)
        cmd = AgentCommand(command='get_current_state')
        retval = self.instrument_agent_client.execute_agent(cmd)
        state = retval.result
        self.assertEqual(state, InstrumentAgentState.INACTIVE)

        cmd = AgentCommand(command='go_active')
        retval = self.instrument_agent_client.execute_agent(cmd)
        cmd = AgentCommand(command='get_current_state')
        retval = self.instrument_agent_client.execute_agent(cmd)
        state = retval.result
        self.assertEqual(state, InstrumentAgentState.IDLE)

        cmd = AgentCommand(command='run')
        retval = self.instrument_agent_client.execute_agent(cmd)
        cmd = AgentCommand(command='get_current_state')
        retval = self.instrument_agent_client.execute_agent(cmd)
        state = retval.result
        self.assertEqual(state, InstrumentAgentState.OBSERVATORY)

        gevent.sleep(5)  # wait for mavs4 to go back to sleep if it was sleeping
        
        # go direct access
        cmd = AgentCommand(command='go_direct_access',
                           kwargs={'session_type': DirectAccessTypes.telnet,
                                   #kwargs={'session_type':DirectAccessTypes.vsp,
                                   'session_timeout':600,
                                   'inactivity_timeout':600})
        retval = self.instrument_agent_client.execute_agent(cmd)
        log.warn("go_direct_access retval=" + str(retval.result))

        # start 'telnet' client with returned address and port
        s = TcpClient(retval.result['ip_address'], retval.result['port'])

        # look for and swallow 'Username' prompt
        while s.peek_at_buffer().find("Username: ") == -1:
            log.debug("WANT 'Username:' READ ==>" + str(s.peek_at_buffer()))
            gevent.sleep(1)
        s.remove_from_buffer("Username: ")
        # send some username string
        s.send_data("bob\r\n", "1")
        
        # look for and swallow 'token' prompt
        while s.peek_at_buffer().find("token: ") == -1:
            log.debug("WANT 'token: ' READ ==>" + str(s.peek_at_buffer()))
            gevent.sleep(1)
        s.remove_from_buffer("token: ")
        # send the returned token
        s.send_data(retval.result['token'] + "\r\n", "1")
        
        # look for and swallow 'connected' indicator
        while s.peek_at_buffer().find("connected\n") == -1:
            log.debug("WANT 'connected\n' READ ==>" + str(s.peek_at_buffer()))
            gevent.sleep(1)
            s.peek_at_buffer()
        s.remove_from_buffer("connected\n")
        
        # try to wake the instrument up from its sleep mode
        n = 0
        s.send_data("\r\n\r\n", "1")
        gevent.sleep(1)
        while s.peek_at_buffer().find("Enter <CTRL>-<C> now to wake up") == -1:
            self.assertNotEqual(n, 5)
            n += 1
            log.debug("WANT 'Enter <CTRL>-<C> now to wake up' READ ==>" + str(s.peek_at_buffer()))
            s.send_data("\r\n\r\n", "1")
            gevent.sleep(1)
            s.peek_at_buffer()
       
        """
        pattern = re.compile("^([ 0-9\-\.]+),([ 0-9\-\.]+),([ 0-9\-\.]+),([ 0-9\-\.]+),([ 0-9\-\.]+),([ 0-9a-z]+),([ 0-9:]+)")

        matches = 0
        n = 0
        while n < 100:
            n = n + 1
            gevent.sleep(1)
            data = s.get_data()
            log.debug("READ ==>" + str(repr(data)))
            m = pattern.search(data)
            if m != None:
                matches = m.lastindex
                if matches == 7:
                    break

        self.assertTrue(matches == 7) # need to have found 7 conformant fields.
        """
        
###############################################################################
# Auto generated code.  There should rarely be reason to edit anything below. #
###############################################################################

"""
these cause nosetest to run all tests twice!
class IntFromIDK(Testmavs4_INT):
    #This class overloads the default test class so that comm configurations can be overloaded.  This is the test class
    #called from the IDK test_driver program
    
    @classmethod
    def init_comm(cls):
        cls.comm_config = CommConfig.get_config_from_file(Metadata()).dict()

class UnitFromIDK(Testmavs4_UNIT):
    #This class overloads the default test class so that comm configurations can be overloaded.  This is the test class
    #called from the IDK test_driver program

    @classmethod
    def init_comm(cls):
        cls.comm_config = CommConfig.get_config_from_file(Metadata()).dict()

class QualFromIDK(Testmavs4_QUAL):
    #This class overloads the default test class so that comm configurations can be overloaded.  This is the test class
    #called from the IDK test_driver program

    @classmethod
    def init_comm(cls):
        cls.comm_config = CommConfig.get_config_from_file(Metadata()).dict()
"""
