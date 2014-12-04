from fabric.api import sudo, settings, parallel

@parallel
def core_machine_settings():
    with settings(connection_attempts=100, timeout=5):
        # increase ulimits
        sudo("chmod 777 /etc/security/limits.conf")
        sudo( 'if ! grep -q "\* soft nofile 20000" /etc/security/limits.conf; then echo "* soft nofile 20000" >> /etc/security/limits.conf; fi')
        sudo('if ! grep -q "\* hard nofile 20000" /etc/security/limits.conf; then echo "* hard nofile 20000" >> /etc/security/limits.conf; fi')
        sudo("chmod 644 /etc/security/limits.conf")

        # install copperegg monitoring

