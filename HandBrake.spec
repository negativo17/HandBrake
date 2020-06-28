#global commit0 bbcd3a5ea70054cef0950c2e0211ab700efce178
#global date 20200331
#global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global tag %{version}

%global desktop_id fr.handbrake.ghb

Name:           HandBrake
Version:        1.3.3
Release:        1%{!?tag:.%{date}git%{shortcommit0}}%{?dist}
Summary:        An open-source multiplatform video transcoder
License:        GPLv2+
URL:            http://handbrake.fr/

%if 0%{?tag:1}
Source0:        https://github.com/%{name}/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
%else
Source0:        https://github.com/%{name}/%{name}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
%endif

# Pass strip tool override to gtk/configure
Patch1:         %{name}-nostrip.patch
# Fix QSV with unpatched system FFmpeg
Patch2:         %{name}-qsv.patch
Patch3:         %{name}-makefile.patch

BuildRequires:  liba52-devel >= 0.7.4
BuildRequires:  cmake
# Should be >= 1.0.8:
BuildRequires:  bzip2-devel
BuildRequires:  dbus-glib-devel
BuildRequires:  desktop-file-utils
# Should be >= 2.12.1:
BuildRequires:  fontconfig-devel >= 2.10.95
BuildRequires:  ffmpeg-devel >= 4.2.1
# Should be >= 2.10.1:
BuildRequires:  freetype-devel >= 2.4.11
# Should be >= 1.0.7:
BuildRequires:  fribidi-devel >= 0.19.4
BuildRequires:  gcc-c++
BuildRequires:  gstreamer1-plugins-base-devel
# Should be >= 2.6.2:
BuildRequires:  harfbuzz-devel >= 1.3.2
BuildRequires:  intel-mediasdk-devel
BuildRequires:  intltool
BuildRequires:  jansson-devel >= 2.10
BuildRequires:  lame-devel >= 3.100
BuildRequires:  libappindicator-gtk3-devel
%if 0%{?fedora}
BuildRequires:  libappstream-glib
%endif
# Should be >= 0.14.0:
BuildRequires:  libass-devel >= 0.13.4
# Should be 1.1.2
BuildRequires:  libbluray-devel >= 1.0.2
# Should be >= 0.5.1:
BuildRequires:  libdav1d-devel >= 0.3.0
BuildRequires:  libdrm-devel
# Should be >= 6.0.1:
BuildRequires:  libdvdnav-devel >= 5.0.3
# Should be >= 6.0.2:
BuildRequires:  libdvdread-devel >= 5.0.3
BuildRequires:  libfdk-aac-devel >= 2.0.1
# On Fedora, libgudev provides libgudev1:
BuildRequires:  libgudev1-devel
BuildRequires:  libva-devel
BuildRequires:  libmpeg2-devel >= 0.5.1
BuildRequires:  libnotify-devel
# Should be >= 1.3.4:
BuildRequires:  libogg-devel >= 1.3.0
BuildRequires:  librsvg2-devel
# Should be >= 0.1.9:
BuildRequires:  libsamplerate-devel >= 0.1.8
BuildRequires:  libtheora-devel >= 1.1.1
BuildRequires:  libtool
BuildRequires:  libva-devel
# Should be >= 1.3.5:
BuildRequires:  libvorbis-devel >= 1.3.3
%if 0%{?rhel} == 7
BuildRequires:  libvpx1.7-devel
%else
BuildRequires:  libvpx-devel >= 1.7.0
%endif
BuildRequires:  libxml2-devel
BuildRequires:  m4
BuildRequires:  make
BuildRequires:  meson
BuildRequires:  nasm
BuildRequires:  nv-codec-headers >= 8.1.24.2
# Should be >= 1.3:
BuildRequires:  opus-devel >= 1.0.2
BuildRequires:  patch
BuildRequires:  pkgconfig(gtk+-3.0) >= 3.16
BuildRequires:  pkgconfig(numa)
BuildRequires:  python3
BuildRequires:  speex-devel >= 1.2
BuildRequires:  subversion
BuildRequires:  tar
BuildRequires:  wget
# Should be >= 155:
BuildRequires:  x264-devel >= 1:0.152
BuildRequires:  x265-devel >= 1:3.2.1
BuildRequires:  zlib-devel
BuildRequires:  xz-devel

Requires:       hicolor-icon-theme

%description
%{name} is a general-purpose, free, open-source, cross-platform, multithreaded
video transcoder software application. It can process most common multimedia
files and any DVD or Bluray sources that do not contain any kind of copy
protection.

%package gui
Summary:        An open-source multiplatform video transcoder (GUI)
Provides:       handbrake-gui = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       handbrake = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       gstreamer1-plugins-good%{_isa}
Requires:       hicolor-icon-theme
Requires:       libdvdcss%{_isa}

%description gui
%{name} is a general-purpose, free, open-source, cross-platform, multithreaded
video transcoder software application. It can process most common multimedia
files and any DVD or Bluray sources that do not contain any kind of copy
protection.

This package contains the main program with a graphical interface.

%package cli
Summary:        An open-source multiplatform video transcoder (CLI)
Provides:       handbrake-cli = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       libdvdcss%{_isa}

%description cli
%{name} is a general-purpose, free, open-source, cross-platform, multithreaded
video transcoder software application. It can process most common multimedia
files and any DVD or Bluray sources that do not contain any kind of copy
protection.

This package contains the command line version of the program.

%prep
%if 0%{?tag:1}
%autosetup -p1
%else
%autosetup -p1 -n %{name}-%{commit0}
%endif
mkdir -p download

# Use system libraries in place of bundled ones
for module in libdav1d fdk-aac ffmpeg libdvdnav libdvdread libbluray libmfx nvenc x265; do
    sed -i -e "/MODULES += contrib\/$module/d" make/include/main.defs
done

# Fix desktop file
sed -i -e 's/%{desktop_id}.svg/%{desktop_id}/g' gtk/src/%{desktop_id}.desktop

%if 0%{?rhel}
# Do not build metainfo data (gettext too old):
sed -i -e '/^metainfo_DATA/g' -e '/^dist_metainfo_DATA/g' gtk/src/Makefile.am
%endif

%build
echo "HASH=%{commit0}" > version.txt
echo "SHORTHASH=%{shortcommit0}" >> version.txt
echo "DATE=$(date "+%Y-%m-%d %T")" >> version.txt
%if 0%{?tag:1}
echo "TAG=%{tag}" >> version.txt
echo "TAG_HASH=%{commit0}" >> version.txt
%endif

# This makes the build stop if any download is attempted
export http_proxy=http://127.0.0.1
export https_proxy=http://127.0.0.1

# By default the project is built with optimizations for speed and no debug.
# Override configure settings by passing RPM_OPT_FLAGS and disabling preset
#p debug options.
%if 0%{?rhel} == 7
echo "GCC.args.O.speed = %{optflags} -I%{_includedir}/ffmpeg -lx265 -lfdk-aac -ldav1d -ldl -lmfx -std=gnu99" > custom.defs
%else
echo "GCC.args.O.speed = %{optflags} -I%{_includedir}/ffmpeg -lx265 -lfdk-aac -ldav1d -ldl -lmfx" > custom.defs
%endif
echo "GCC.args.g.none = " >> custom.defs
echo "GCC.args.strip = " >> custom.defs

# Not an autotools configure script.
./configure \
    --build build \
    --disable-df-fetch \
    --disable-df-verify \
    --disable-update-checks \
    --enable-asm \
    --enable-fdk-aac \
    --enable-gst \
    --enable-numa \
    --enable-nvenc \
    --enable-qsv \
    --enable-x265 \
    --prefix=%{_prefix}

%make_build -C build

%install
%make_install -C build

# Desktop file, icons from FlatPak build (more complete)
rm -f %{buildroot}/%{_datadir}/applications/ghb.desktop \
    %{buildroot}/%{_datadir}/icons/hicolor/scalable/apps/hb-icon.svg

install -D -p -m 644 gtk/src/%{desktop_id}.desktop \
    %{buildroot}/%{_datadir}/applications/%{desktop_id}.desktop
install -D -p -m 644 gtk/src/%{desktop_id}.svg \
    %{buildroot}/%{_datadir}/icons/hicolor/scalable/apps/%{desktop_id}.svg


%if 0%{?rhel}
rm -fr %{buildroot}%{_datadir}/metainfo
%endif

%find_lang ghb

%check
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{desktop_id}.desktop
%if 0%{?fedora}
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{desktop_id}.metainfo.xml
%endif

%if 0%{?rhel} == 7
%post gui
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
/usr/bin/update-desktop-database &> /dev/null || :

%postun gui
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
/usr/bin/update-desktop-database &> /dev/null || :

%posttrans gui
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
%endif

%files -f ghb.lang gui
%license COPYING
%doc AUTHORS.markdown NEWS.markdown README.markdown THANKS.markdown
%{_bindir}/ghb
%if 0%{?fedora}
%{_metainfodir}/%{desktop_id}.metainfo.xml
%endif
%{_datadir}/applications/%{desktop_id}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{desktop_id}.svg

%files cli
%license COPYING
%doc AUTHORS.markdown NEWS.markdown README.markdown THANKS.markdown
%{_bindir}/HandBrakeCLI

%changelog
* Tue Jun 23 2020 Simone Caronni <negativo17@gmail.com> - 1.3.3-1
- Update to 1.3.3.
- Add temporary patch to Makefile.
- Trim changelog.
- Disable metainfo generation on CentOS/RHEL 7/8 as gettext is too old.

* Fri May 15 2020 Simone Caronni <negativo17@gmail.com> - 1.3.2-1
- Update to 1.3.2 release.

* Wed Apr 15 2020 Simone Caronni <negativo17@gmail.com> - 1.3.1-4.20200331gitbbcd3a5
- Update to latest 1.3.x branch snapshot.
- Enable Intel QuickSync support.

* Wed Mar 18 2020 Simone Caronni <negativo17@gmail.com> - 1.3.1-3
- Rebuild for updated dependencies.

* Sun Jan 19 2020 Simone Caronni <negativo17@gmail.com> - 1.3.1-2
- Rebuild for updated dependencies.

* Sun Jan 12 2020 Simone Caronni <negativo17@gmail.com> - 1.3.1-1
- Update to 1.3.1.

* Mon Dec 09 2019 Simone Caronni <negativo17@gmail.com> - 1.3.0-1
- Update to 1.3.0.

* Wed Nov 27 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-8.20191031gita5d359d
- Update to latest snapshot.

* Fri Nov 01 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-7.20191031gitad8cf9f
- Update to latest snapshot.
- Momentarily disable QSV encoder.

* Sun Oct 20 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-6.20191018git9901594
- Udpate to latest snapshot and dependencies.

* Sat Sep 14 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-5.20190914gite2a9571
- Update to latest snapshot.

* Thu Sep 12 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-4
- Add patches from the 1.2.x branch.

* Sun Jul 07 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-3
- Rebuild for updated dependencies.

* Mon May 27 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-2
- Rebuild for updated dependencies.

* Sun Mar 03 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-1
- Update to 1.2.2.

* Thu Feb 28 2019 Simone Caronni <negativo17@gmail.com> - 1.2.1-2
- Rebuild for updated dependencies.

* Sat Feb 23 2019 Simone Caronni <negativo17@gmail.com> - 1.2.1-1
- Update to 1.2.1.
- Do not install AppData file on RHEL < 8.
