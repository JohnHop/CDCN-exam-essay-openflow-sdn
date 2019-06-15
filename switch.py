from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()


class Tutorial (object):
  """
  A Tutorial object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

    # Use this table to keep track of which ethernet address is on
    # which switch port (keys are MACs, values are ports).
    self.mac_to_port = {}


  def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in

    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)


  def act_like_switch (self, packet, packet_in):
    """
    Implement switch-like behavior.
    """

    # Here's some psuedocode to start you off implementing a learning
    # switch.  You'll need to rewrite it as real Python code.

    # Learn the port for the source MAC
    switchInputPort = packet_in.in_port

    self.mac_to_port[packet.src] = switchInputPort      #self.mac_to_port ... <add or update entry>

    #if the port associated with the destination MAC of the packet is known:
    if packet.dst in self.mac_to_port:
      # Send packet out the associated port
      #self.resend_packet(packet_in, self.mac_to_port[packet.dst])

      # Once you have the above working, try pushing a flow entry
      # instead of resending the packet (comment out the above and
      # uncomment and complete the below.)

      log.debug("Installing flow...")
      log.debug(str(packet_in.in_port)+"/"+str(packet.src)+"/"+str(packet.dst)+" => "+str(self.mac_to_port[packet.dst])+"\n")

      msg = of.ofp_flow_mod()

      # Set fields to match received packet
      msg.match = of.ofp_match.from_packet(packet, packet_in.in_port)

      #< Set other fields of flow_mod (timeouts? buffer_id?) >      
      msg.buffer_id = packet_in.buffer_id

      #< Add an output action, and send -- similar to resend_packet() >
      msg.actions.append(of.ofp_action_output(port = self.mac_to_port[packet.dst]))
      self.connection.send(msg)
    
    else:
      # Flood the packet out everything but the input port
      # This part looks familiar, right?
      self.resend_packet(packet_in, of.OFPP_ALL)



	def _handle_PacketIn (self, event):
		 """
		 Handles packet in messages from the switch.
		 """

		 packet = event.parsed # This is the parsed packet data.
		 if not packet.parsed:
		   log.warning("Ignoring incomplete packet")
		   return

		 packet_in = event.ofp # The actual ofp_packet_in message.

		 # Comment out the following line and uncomment the one after
		 # when starting the exercise.

		 #self.act_like_hub(packet, packet_in)
		 self.act_like_switch(packet, packet_in)



def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Tutorial(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)

