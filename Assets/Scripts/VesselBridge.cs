using System;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using Newtonsoft.Json;

public class VesselBridge : MonoBehaviour
{
    public string serverIP = "127.0.0.1";
    public int port = 5555;
    private TcpClient client;
    private NetworkStream stream;

    [Serializable]
    public class Packet {
        public string type;
        public object data;
        public string signature;
    }

    public void SendAction(string actionType, object payload, string hmac)
    {
        try {
            client = new TcpClient(serverIP, port);
            stream = client.GetStream();

            Packet p = new Packet { type = actionType, data = payload, signature = hmac };
            string json = JsonConvert.SerializeObject(p);
            byte[] buffer = Encoding.UTF8.GetBytes(json);

            stream.Write(buffer, 0, buffer.Length);
            
            // Receive updated state
            byte[] receiveBuffer = new byte[8192];
            int bytesRead = stream.Read(receiveBuffer, 0, receiveBuffer.Length);
            string response = Encoding.UTF8.GetString(receiveBuffer, 0, bytesRead);
            
            ProcessResponse(response);
        }
        catch (Exception e) {
            Debug.LogError($"Bridge Error: {e.Message}");
        }
        finally {
            stream?.Close();
            client?.Close();
        }
    }

    private void ProcessResponse(string jsonResponse)
    {
        // Updates the 3D transforms based on Authoritative Python data
        var update = JsonConvert.DeserializeObject<dynamic>(jsonResponse);
        VesselManager.Instance.SyncVessels(update.results);
    }
}