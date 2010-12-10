from astrometry.util.pyfits_utils import *
from numpy import *
import pyfits

def sdss_tsfield_get_node_incl(tsfield):
	hdr = tsfield[0].header
	node = deg2rad(hdr.get('NODE'))
	incl = deg2rad(hdr.get('INCL'))
	return (node, incl)

def sdss_munu_to_radec(mu, nu, tsfield):
	node, incl = sdss_tsfield_get_node_incl(tsfield)
	mu, nu = deg2rad(mu), deg2rad(nu)
	ra = node + arctan2(sin(mu - node) * cos(nu) * cos(incl) - sin(nu) * sin(incl), cos(mu - node) * cos(nu))
	dec = arcsin(sin(mu - node) * cos(nu) * sin(incl) + sin(nu) * cos(incl))
	ra, dec = rad2deg(ra), rad2deg(dec)
	ra += (360. * (ra < 0))
	return (ra, dec)


def sdss_radec_to_munu(ra, dec, tsfield):
	node, incl = sdss_tsfield_get_node_incl(tsfield)
	ra, dec = deg2rad(ra), deg2rad(dec)
	mu = node + arctan2(sin(ra - node) * cos(dec) * cos(incl) + sin(dec) * sin(incl), cos(ra - node) * cos(dec))
	nu = arcsin(-sin(ra - node) * cos(dec) * sin(incl) + sin(dec) * cos(incl))
	mu, nu = rad2deg(mu), rad2deg(nu)
	mu += (360. * (mu < 0))
	return (mu, nu)

def sdss_pixel_to_radec(x, y, color, band, tsfield):
	mu, nu = sdss_pixel_to_munu(x, y, color, band, tsfield)
	return sdss_munu_to_radec(mu, nu, tsfield)

def sdss_prime_to_pixel(xprime, yprime,  color, band, tsfield):
	T = fits_table(tsfield[1].data)
	T = T[0]

	color0 = T.ricut[band]
	g0, g1, g2, g3 = T.drow0[band], T.drow1[band], T.drow2[band], T.drow3[band]
	h0, h1, h2, h3 = T.dcol0[band], T.dcol1[band], T.dcol2[band], T.dcol3[band]
	px, py = T.csrow[band], T.cscol[band]
	qx, qy = T.ccrow[band], T.cccol[band]

	color  = atleast_1d(color)
	color0 = atleast_1d(color0)
	xprime -= where(color < color0, px * color, qx)
	yprime -= where(color < color0, py * color, qy)

	# Now invert:
	#   xprime = x + g0 + g1 * y + g2 * y**2 + g3 * y**3
	#   yprime = y + h0 + h1 * y + h2 * y**2 + h3 * y**3

	y = yprime
	while True:
		yp = y + h0 + h1 * y + h2 * y**2 + h3 * y**3
		dypdy = 1 + h1 + h2 * 2*y + h3 * 3*y**2
		dy = (yprime - yp) / dypdy
		y -= dy
		#if (dy 

	x = xprime - (g0 + g1 * y + g2 * y**2 + g3 * y**3)



	pass

def sdss_pixel_to_prime(x, y, color, band, tsfield):
	T = fits_table(tsfield[1].data)
	T = T[0]

	# Secret decoder ring:
	#  http://www.sdss.org/dr7/products/general/astrometry.html
	# (color)0 is called riCut;
	# g0, g1, g2, and g3 are called
	#    dRow0, dRow1, dRow2, and dRow3, respectively;
	# h0, h1, h2, and h3 are called
	#    dCol0, dCol1, dCol2, and dCol3, respectively;
	# px and py are called csRow and csCol, respectively;
	# and qx and qy are called ccRow and ccCol, respectively.

	color0 = T.ricut[band]
	g0, g1, g2, g3 = T.drow0[band], T.drow1[band], T.drow2[band], T.drow3[band]
	h0, h1, h2, h3 = T.dcol0[band], T.dcol1[band], T.dcol2[band], T.dcol3[band]
	px, py = T.csrow[band], T.cscol[band]
	qx, qy = T.ccrow[band], T.cccol[band]

	print 'px,py', px,py
	print 'qx,qy', qx,qy
	print 'color0', color0

	xprime = x + g0 + g1 * y + g2 * y**2 + g3 * y**3
	yprime = y + h0 + h1 * y + h2 * y**2 + h3 * y**3

	'''
	if color < color0:
		xprime += px * color
		yprime += py * color
	else:
		xprime += qx
		yprime += qy
	'''
	color  = atleast_1d(color)
	color0 = atleast_1d(color0)
	xprime += where(color < color0, px * color, qx)
	yprime += where(color < color0, py * color, qy)
	return (xprime, yprime)


def sdss_pixel_to_munu(x, y, color, band, tsfield):
	T = fits_table(tsfield[1].data)
	T = T[0]

	(xprime, yprime) = sdss_pixel_to_prime(x, y, color, band, tsfield)

	a, b, c = T.a[band], T.b[band], T.c[band]
	d, e, f = T.d[band], T.e[band], T.f[band]

	mu = a + b * xprime + c * yprime
	nu = d + e * xprime + f * yprime

	return (mu, nu)
	


if __name__ == '__main__':
	tsfield = pyfits.open('tsField-002830-6-41-0398.fit')

	x,y = 0,0
	band = array([2,3])
	color = 0.
	rd = sdss_pixel_to_radec(x, y, color, band, tsfield)
	print rd

	N = 10
	x = numpy.random.uniform(2048, size=(N,))
	y = numpy.random.uniform(1489, size=(N,))
	color = numpy.random.uniform(-1, 4, size=(N,))
	band = 2
	rd = sdss_pixel_to_radec(x, y, color, band, tsfield)
	print rd

	m,n = numpy.random.uniform(360, size=N), numpy.random.uniform(-90, 90, size=N)
	r,d = sdss_munu_to_radec(m, n, tsfield)
	#print r,d
	mu,nu = sdss_radec_to_munu(r, d, tsfield)
	print mu-m, nu-n
