param([string]$adapterName)

# Encontrar adaptador de rede por nome
$adapter = Get-NetAdapter | Where-Object {$_.Name -like "*$adapterName*" -or $_.InterfaceDescription -like "*$adapterName*"}

if ($adapter -eq $null) {
    Write-Host "Adaptador não encontrado: $adapterName"
    exit 1
}

Write-Host "Adaptador encontrado: $($adapter.Name) - $($adapter.InterfaceDescription)"

# Desativar offloads e otimizações que podem afetar latência
$properties = @(
    @{Name="*EEE"; Value=0; Description="Energy-Efficient Ethernet"},
    @{Name="*FlowControl"; Value=0; Description="Flow Control"},
    @{Name="*InterruptModeration"; Value=0; Description="Interrupt Moderation"},
    @{Name="*PriorityVLANTag"; Value=1; Description="Packet Priority"},
    @{Name="*ReceiveBuffers"; Value=256; Description="Receive Buffers"},
    @{Name="*TransmitBuffers"; Value=256; Description="Transmit Buffers"},
    @{Name="*TCPChecksumOffloadIPv4"; Value=0; Description="TCP Checksum Offload IPv4"},
    @{Name="*TCPChecksumOffloadIPv6"; Value=0; Description="TCP Checksum Offload IPv6"},
    @{Name="*UDPChecksumOffloadIPv4"; Value=0; Description="UDP Checksum Offload IPv4"},
    @{Name="*UDPChecksumOffloadIPv6"; Value=0; Description="UDP Checksum Offload IPv6"},
    @{Name="*PMARPOffload"; Value=0; Description="ARP Offload"},
    @{Name="*PMNSOffload"; Value=0; Description="NS Offload"},
    @{Name="*AutoPowerSaveModeEnabled"; Value=0; Description="Auto Power Save Mode"},
    @{Name="EnablePME"; Value=0; Description="Wake on Magic Packet"},
    @{Name="*JumboPacket"; Value=0; Description="Jumbo Packet"}
)

foreach ($prop in $properties) {
    try {
        $name = $prop.Name
        $value = $prop.Value
        $desc = $prop.Description
        
        # Verificar se a propriedade existe para este adaptador
        $adapterProperty = Get-NetAdapterAdvancedProperty -Name $adapter.Name -DisplayName $desc -ErrorAction SilentlyContinue
        
        if ($adapterProperty) {
            # Propriedade existe, tentar definir
            Set-NetAdapterAdvancedProperty -Name $adapter.Name -DisplayName $desc -DisplayValue $value -ErrorAction SilentlyContinue
            Write-Host "Configuração aplicada: $desc = $value"
        } else {
            # Tentar outra abordagem com o nome exato da propriedade
            $adapterProperty = Get-NetAdapterAdvancedProperty -Name $adapter.Name | Where-Object { $_.RegistryKeyword -eq $name } -ErrorAction SilentlyContinue
            
            if ($adapterProperty) {
                # Propriedade encontrada pelo nome de registro
                Set-NetAdapterAdvancedProperty -Name $adapter.Name -RegistryKeyword $name -RegistryValue $value -ErrorAction SilentlyContinue
                Write-Host "Configuração aplicada (via registro): $name = $value"
            } else {
                Write-Host "Propriedade não encontrada: $desc ($name)"
            }
        }
    } catch {
        Write-Host "Erro ao configurar $($prop.Description): $_"
    }
}
