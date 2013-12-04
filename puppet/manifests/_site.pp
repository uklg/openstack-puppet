$pvolume='/dev/sdb'
$vgroup='cinder-volumes'

notify{"${hostname}":}
notify{"${ipaddress}":}

host { "${hostname}":
    ensure => 'present',       
    target => '/etc/hosts',    
    ip => "${ipaddress}",         
}


package { 'lvm2':
    ensure => 'installed'
}

physical_volume { "${pvolume}":
    ensure => present,
}

volume_group {  "${vgroup}": 
    ensure => present,
    physical_volumes => "${pvolume}"
}

exec { '/etc/puppet/manifests/far_lvm.conf.py': require => Package['lvm2'] }
