#pragma once

#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#include <iostream>
#include <sstream>

class TcpSender
{
public:
  // public member variables

  std::string dest_ip; /**< destination ip address */
  uint16_t dest_port;  /**< destination port number */
  bool verbose;        /**< set on if you want debug prints */

  // public member functions

  /**
   * normal constructor
   * sets default destination ip/port to user specified values
   */
  TcpSender(std::string ip, uint16_t port)
  {
    // default verbose off
    verbose = false;

    dest_ip = ip;
    dest_port = port;

    recv_buff_len = 1024;
    recv_buff = new char[recv_buff_len];

    // initialize socket
    init_socket(dest_ip, dest_port);
  }
  /**
   * destructor
   */
  ~TcpSender() {}

  void send()
  {
  }

private:
  // private member variables
  int sock_fd;             /**< socket file descriptor */
  char *recv_buff;         /**< receive buffer */
  uint16_t recv_buff_len;  /**< length of receive buffer */
  struct sockaddr_in dest; /**< destination address socket info */

  // private member functions
};

int main()
{
  TcpSender sender("127.0.0.1", 6942);
  sender.send();
}